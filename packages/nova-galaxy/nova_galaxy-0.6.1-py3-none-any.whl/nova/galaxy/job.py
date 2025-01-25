"""Internal job related classes and functions."""

import sys
import time
from threading import Thread
from typing import TYPE_CHECKING, Dict, Optional

from bioblend import galaxy

if TYPE_CHECKING:
    from .data_store import Datastore
from .dataset import AbstractData, Dataset, DatasetCollection, upload_datasets
from .outputs import Outputs
from .parameters import Parameters
from .util import WorkState


class JobStatus:
    """Internal structure to hold job status info."""

    def __init__(self) -> None:
        self.state = WorkState.NOT_STARTED
        self.details = ""
        self.error_msg = ""


class Job:
    """Internal class managing Galaxy job execution. Should not be used by end users."""

    def __init__(self, tool_id: str, data_store: "Datastore") -> None:
        self.id = ""
        self.datasets = None
        self.collections = None
        self.tool = tool_id
        self.store = data_store
        self.galaxy_instance = self.store.nova_connection.galaxy_instance
        self.status = JobStatus()
        self.url: Optional[str] = None

    def _run_and_wait(self, params: Optional[Parameters]) -> None:
        """Runs tools and waits for result."""
        self.submit(params)
        try:
            self.wait_for_results()
        except Exception:
            self.url = None
            self.status.state = WorkState.ERROR

        self.status.state = WorkState.FINISHED

    def run(self, params: Optional[Parameters], wait: bool) -> Optional[Outputs]:
        """Runs a job in Galaxy."""
        if self.status.state in [WorkState.NOT_STARTED, WorkState.FINISHED, WorkState.ERROR]:
            thread = Thread(target=self._run_and_wait, args=(params,))
            thread.start()
            if wait:
                thread.join()
                return self.get_results()
            return None
        else:
            raise Exception(f"Tool {self.tool} (id: {self.id}) is already running.")

    def run_interactive(
        self, params: Optional[Parameters], wait: bool, max_tries: int = 100, check_url: bool = True
    ) -> Optional[str]:
        """Runs an interactive tool in Galaxy and returns a link to the tool."""
        self.run(params, False)
        if not wait:
            return None
        successful_url = self.get_url(max_tries=max_tries, check_url=check_url)
        if successful_url:
            return successful_url
        # If successful_url is None, then there was an issue starting the interactive tool.
        status = self.cancel()
        # if status is false, the job has been in a terminal state already, indicating an error somewhere in execution.
        if status:
            raise Exception(
                "Unable to fetch the URL for interactive tool. This could be due to needing to pull the docker image. "
                "Try again with a larger 'max_tries' value."
            )
        else:
            raise Exception("Interactive tool was stopped unexpectedly.")

    def submit(self, params: Optional[Parameters]) -> None:
        """Handles uploading inputs and submitting job."""
        self.status.state = WorkState.UPLOADING_DATA
        self.url = None
        datasets_to_upload = {}

        # Set Tool Inputs
        tool_inputs = galaxy.tools.inputs.inputs()
        if params:
            for param, val in params.inputs.items():
                if isinstance(val, AbstractData):
                    datasets_to_upload[param] = val
                else:
                    tool_inputs.set_param(param, val)
            ids = upload_datasets(store=self.store, datasets=datasets_to_upload)
            for param, val in ids.items():
                tool_inputs.set_dataset_param(param, val)

        # Run tool and wait for job to finish
        self.status.state = WorkState.QUEUED
        results = self.galaxy_instance.tools.run_tool(
            history_id=self.store.history_id, tool_id=self.tool, tool_inputs=tool_inputs
        )
        self.id = results["jobs"][0]["id"]
        self.datasets = results["outputs"]
        self.collections = results["output_collections"]

    def cancel(self, check_results: bool = False) -> bool:
        """Cancels or stops a job in Galaxy."""
        self.url = None
        if check_results:
            response = self.galaxy_instance.make_get_request(
                f"{self.store.nova_connection.galaxy_url}/api/jobs{self.id}/finish"
            )
            if response.status_code == 200:
                self.status.state = WorkState.FINISHED
                return True
            else:
                self.status.state = WorkState.FINISHED
                self.status.error_msg = response.text
                return False
        self.status.state = WorkState.ERROR
        return self.galaxy_instance.jobs.cancel_job(self.id)

    def wait_for_results(self) -> None:
        """Wait for job to finish."""
        self.galaxy_instance.jobs.wait_for_job(self.id)

    def get_state(self) -> JobStatus:
        """Returns current state of job."""
        if self.status.state == WorkState.QUEUED:
            job = self.galaxy_instance.jobs.show_job(self.id)
            if job["state"] == "running":
                self.status.state = WorkState.RUNNING
        return self.status

    def get_results(self) -> Outputs:
        """Return results from finished job."""
        if self.status.state == WorkState.FINISHED:
            outputs = Outputs()
            if self.datasets:
                for dataset in self.datasets:
                    d = Dataset(dataset["output_name"])
                    d.id = dataset["id"]
                    d.store = self.store
                    outputs.add_output(d)
            if self.collections:
                for collection in self.collections:
                    dc = DatasetCollection(collection["output_name"])
                    dc.id = collection["id"]
                    dc.store = self.store
                    outputs.add_output(dc)

            return outputs
        else:
            raise Exception(f"Job {self.id} has not finished running.")

    def get_url(self, max_tries: int = 100, check_url: bool = True) -> Optional[str]:
        """Get the URL or endpoint for this tool."""
        if self.url:
            return self.url
        timer = max_tries
        while timer > 0:
            try:
                entry_points = self.galaxy_instance.make_get_request(
                    f"{self.store.nova_connection.galaxy_url}/api/entry_points?job_id={self.id}"
                )
                for ep in entry_points.json():
                    if ep["job_id"] == self.id and ep.get("target", None):
                        url = f"{self.store.nova_connection.galaxy_url}{ep['target']}"
                        self.url = url
                        response = self.galaxy_instance.make_get_request(url)
                        if response.status_code == 200 or not check_url:
                            return url
            except Exception:
                continue
            finally:
                timer -= 1
                time.sleep(1)
        return None

    def get_console_output(self) -> Dict[str, str]:
        """Get all the current console output."""
        out = self.galaxy_instance.make_get_request(
            f"{self.store.nova_connection.galaxy_url}/api/jobs/"
            f"{self.id}/console_output?stdout_position=0&stdout_length="
            f"{sys.maxsize - 1}&stderr_position=0&stderr_length={sys.maxsize - 1}"
        )
        out.raise_for_status()
        return out.json()
