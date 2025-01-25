"""Main module to run and monitor a pipeline."""

import json
import logging
import re
from datetime import datetime
from typing import Dict, Optional
from urllib.request import urlopen
from zoneinfo import ZoneInfo

import requests

try:
    from aind_alert_utils.teams import create_body_contents
    from aind_data_schema_models.data_name_patterns import DataLevel, DataRegex
except ModuleNotFoundError:  # pragma: no cover
    raise ModuleNotFoundError(
        "Running jobs requires all dependencies: "
        "'pip install aind-codeocean-pipeline-monitor[full]'. "
        "See README for more information."
    )
from codeocean import CodeOcean
from codeocean.computation import Computation, ComputationState
from codeocean.data_asset import (
    AWSS3Target,
    ComputationSource,
    DataAsset,
    DataAssetParams,
    DataAssetState,
    Source,
    Target,
)

from aind_codeocean_pipeline_monitor.models import PipelineMonitorSettings


class PipelineMonitorJob:
    """Class to run a PipelineMonitor Job"""

    def __init__(
        self, job_settings: PipelineMonitorSettings, client: CodeOcean
    ):
        """Class constructor"""
        self.job_settings = job_settings
        self.client = client

    def _monitor_pipeline(self, computation: Computation) -> Computation:
        """
        Monitor a pipeline. Will retry requests if TooManyRequests.
        Parameters
        ----------
        computation : Computation
          Computation from _start_pipeline response

        Returns
        -------
        Computation

        """
        try:
            wait_until_completed_response = (
                self.client.computations.wait_until_completed(
                    computation=computation,
                    polling_interval=(
                        self.job_settings.computation_polling_interval
                    ),
                    timeout=self.job_settings.computation_timeout,
                )
            )
            if wait_until_completed_response.state == ComputationState.Failed:
                raise Exception(
                    f"The pipeline run failed: {wait_until_completed_response}"
                )
            return wait_until_completed_response
        except TimeoutError as e:
            logging.error(
                f"Computation timeout reached: {e.args}, attempting to "
                f"terminate pipeline"
            )
            self.client.computations.delete_computation(
                computation_id=computation.id
            )
            raise e

    def _wait_for_data_asset(self, create_data_asset_response) -> DataAsset:
        """
        Wait for data asset to be available. Will retry if TooManyRequests.
        Parameters
        ----------
        create_data_asset_response : DataAsset

        Returns
        -------

        """
        wait_until_ready_response = self.client.data_assets.wait_until_ready(
            data_asset=create_data_asset_response,
            polling_interval=(
                self.job_settings.data_asset_ready_polling_interval
            ),
            timeout=self.job_settings.data_asset_ready_timeout,
        )
        if wait_until_ready_response.state == DataAssetState.Failed:
            raise Exception(
                f"Data asset creation failed: {wait_until_ready_response}"
            )
        return wait_until_ready_response

    def _send_alert_to_teams(
        self, message: str, extra_text: Optional[str] = None
    ):
        """
        Send an alert to MS Teams.

        Parameters
        ----------
        message : str
        extra_text : Optional[str]

        """

        post_request_contents = create_body_contents(
            message=message, extra_text=extra_text
        )
        response = requests.post(
            url=self.job_settings.alert_url, json=post_request_contents
        )
        if response.status_code == 200:
            logging.info(f"Alert response: {response.json()}")
        else:
            logging.warning(
                f"There was an issue sending the alert: {response}"
            )

    def _get_input_data_name(self) -> Optional[str]:
        """Get the name of the input data asset from the run_params"""

        input_data_assets = self.job_settings.run_params.data_assets
        if input_data_assets:
            first_data_asset = input_data_assets[0]
            input_data_asset = self.client.data_assets.get_data_asset(
                data_asset_id=first_data_asset.id
            )
            return input_data_asset.name
        else:
            return None

    def _get_name_and_level_from_data_description(
        self, computation: Computation
    ) -> Dict[str, Optional[str]]:
        """
        Attempts to download a data_description file from the 'results' folder
        and then extracts the 'name' and 'data_level' from that file.

        Parameters
        ----------
        computation : Computation

        Returns
        -------
        Dict[str, Optional[str]]
          {'name': Optional[str], 'data_level': Optional[str]}

        """

        dd_file_name = (
            self.job_settings.capture_settings.data_description_file_name
        )

        result_files = self.client.computations.list_computation_results(
            computation_id=computation.id
        )

        if dd_file_name in [r.path for r in result_files.items]:
            download_url = (
                self.client.computations.get_result_file_download_url(
                    computation_id=computation.id,
                    path=dd_file_name,
                )
            )
            with urlopen(download_url.url) as f:
                contents = f.read().decode("utf-8")
            data_description = json.loads(contents)
            return {
                "name": data_description.get("name"),
                "data_level": data_description.get("data_level"),
            }
        else:
            return {"name": None, "data_level": None}

    def _get_name(
        self, computation: Computation, input_data_name: Optional[str]
    ) -> str:
        """
        Get a data asset name. Will try to use the name from a
        data_description.json file. If file does not exist, then will build a
        default name using the input_data_name, process_name_suffix, and
        process_name_suffix_tz fields defined in CapturedDataAssetParams.

        Parameters
        ----------
        computation : Computation
          Uses the computation.id and the code ocean sdk to check if there is
          a data_description.json file in the results folder. Will attempt to
          extract the data_asset_name from that file if found. Otherwise, this
          method will construct a default name using the input data_asset and
          the current datetime in utc.
        input_data_name : Optional[str]
          Name of the input data asset. The computation only stores the id.

        Returns
        -------
        str

        """

        capture_params = self.job_settings.capture_settings
        dt = datetime.now(
            tz=ZoneInfo(
                self.job_settings.capture_settings.process_name_suffix_tz
            )
        )
        suffix = capture_params.process_name_suffix
        dt_suffix = dt.strftime("%Y-%m-%d_%H-%M-%S")

        default_name = f"{input_data_name}_{suffix}_{dt_suffix}"

        info_from_file = self._get_name_and_level_from_data_description(
            computation=computation
        )
        name_from_file = info_from_file.get("name")
        level_from_file = info_from_file.get("data_level")
        if level_from_file != DataLevel.DERIVED.value:
            logging.warning(
                f"Data level in data description {level_from_file} "
                f"does not match expected pattern! Ignoring name in data "
                f"description and will attempt to set a default name."
            )
            name_from_file = None
        elif (
            name_from_file is not None
            and re.match(DataRegex.DERIVED.value, name_from_file) is None
        ):
            logging.warning(
                f"Name in data description {name_from_file} "
                f"does not match expected pattern! "
                f"Will attempt to set default."
            )
            name_from_file = None

        if name_from_file is None and input_data_name is None:
            raise Exception("Unable to construct data asset name.")
        elif name_from_file is not None:
            return name_from_file
        else:
            return default_name

    def _build_data_asset_params(
        self,
        monitor_pipeline_response: Computation,
        input_data_name: Optional[str],
    ) -> DataAssetParams:
        """
        Build DataAssetParams model from CapturedDataAssetParams and
        Computation from monitor_pipeline_response

        Parameters
        ----------
        monitor_pipeline_response : Computation
          The Computation from monitor_pipeline_response. If Target is set to
          AWSS3Target, prefix will be overridden with data asset name.
        input_data_name : Optional[str]

        Returns
        -------
        DataAssetParams

        """
        if self.job_settings.capture_settings.name is not None:
            data_asset_name = self.job_settings.capture_settings.name
        else:
            data_asset_name = self._get_name(
                computation=monitor_pipeline_response,
                input_data_name=input_data_name,
            )
        if self.job_settings.capture_settings.mount is not None:
            data_asset_mount = self.job_settings.capture_settings.mount
        else:
            data_asset_mount = data_asset_name
        if self.job_settings.capture_settings.target is not None:
            prefix = data_asset_name
            bucket = self.job_settings.capture_settings.target.aws.bucket
            target = Target(aws=AWSS3Target(bucket=bucket, prefix=prefix))
        else:
            target = None

        data_asset_params = DataAssetParams(
            name=data_asset_name,
            description=self.job_settings.capture_settings.description,
            mount=data_asset_mount,
            tags=self.job_settings.capture_settings.tags,
            source=Source(
                computation=ComputationSource(
                    id=monitor_pipeline_response.id,
                ),
            ),
            target=target,
            custom_metadata=(
                self.job_settings.capture_settings.custom_metadata
            ),
            results_info=self.job_settings.capture_settings.results_info,
        )
        return data_asset_params

    def run_job(self):
        """
        Run pipeline monitor job. If captured_data_asset_params is not
        None, then will capture result.
        """

        input_data_name = self._get_input_data_name()
        try:
            logging.info(
                f"Starting job with: {self.job_settings}. "
                f"Input data: {input_data_name}"
            )
            if self.job_settings.alert_url is not None:
                message = f"Starting {input_data_name}"
                self._send_alert_to_teams(message=message)

            start_pipeline_response = self.client.computations.run_capsule(
                self.job_settings.run_params
            )
            logging.info(f"start_pipeline_response: {start_pipeline_response}")
            monitor_pipeline_response = self._monitor_pipeline(
                start_pipeline_response
            )
            logging.info(
                f"monitor_pipeline_response: {monitor_pipeline_response}"
            )
            if self.job_settings.capture_settings is not None:
                logging.info("Capturing result")
                data_asset_params = self._build_data_asset_params(
                    monitor_pipeline_response=monitor_pipeline_response,
                    input_data_name=input_data_name,
                )
                capture_result_response = (
                    self.client.data_assets.create_data_asset(
                        data_asset_params=data_asset_params
                    )
                )
                logging.info(
                    f"capture_result_response: {capture_result_response}"
                )
                wait_for_data_asset = self._wait_for_data_asset(
                    create_data_asset_response=capture_result_response
                )
                logging.info(
                    f"wait_for_data_asset_response: {wait_for_data_asset}"
                )
                self.client.data_assets.update_permissions(
                    data_asset_id=capture_result_response.id,
                    permissions=self.job_settings.capture_settings.permissions,
                )
            logging.info("Finished job.")
            if self.job_settings.alert_url is not None:
                message = f"Finished {input_data_name}"
                self._send_alert_to_teams(message=message)
        except Exception as e:
            if self.job_settings.alert_url is not None:
                message = f"Error with {input_data_name}"
                extra_text = f"Message: {e.args}"
                self._send_alert_to_teams(
                    message=message, extra_text=extra_text
                )
            raise e
