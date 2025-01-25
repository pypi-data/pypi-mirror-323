"""Contains classes to run tools in Galaxy via Nova."""

from typing import TYPE_CHECKING, List, Optional, Union

if TYPE_CHECKING:
    from .data_store import Datastore  # Only imports for type checking

from .dataset import AbstractData
from .job import Job
from .outputs import Outputs
from .parameters import Parameters
from .util import WorkState


class AbstractWork:
    """Abstraction for a runnable object in Galaxy such as a tool or workflow."""

    def __init__(self, id: str):
        self.id = id

    def get_outputs(self) -> List[AbstractData]:
        return []

    def get_inputs(self) -> List[Parameters]:
        return []

    def run(self, data_store: "Datastore", params: Parameters, wait: bool) -> Union[Outputs, None]:
        return None


class Tool(AbstractWork):
    """Represents a tool from Galaxy that can be run.

    It's recommended to create a new Tool object every time you want to run a tool to prevent results from being
    overridden.

    """

    def __init__(self, id: str):
        super().__init__(id)
        self._job: Optional[Job] = None

    def run(self, data_store: "Datastore", params: Optional[Parameters] = None, wait: bool = True) -> Optional[Outputs]:
        """Run this tool.

        By default, will be run in a blocking manner, unless `wait` is set to False. Will return the
        results as an instance of the `Outputs` class from nova.galaxy.outputs if run in a blocking way. Otherwise, will
        return None, and the user will be responsible for getting results by calling `get_results`.

        Parameters
        ----------
        data_store: Datastore
            The data store to run this tool in.
        params: Parameters
            The input parameters for this tool.
        wait: bool
            Whether to run this tool in a blocking manner (True) or not (False). Default is True.

        Returns
        -------
        Optional[Outputs]
            If run in a blocking manner, returns the Outputs once the tool is finished running. Otherwise, returns None.

        """
        self._job = Job(self.id, data_store)
        return self._job.run(params, wait)

    def run_interactive(
        self,
        data_store: "Datastore",
        params: Optional[Parameters] = None,
        wait: bool = True,
        max_tries: int = 100,
        check_url: bool = True,
    ) -> Optional[str]:
        """Run tool interactively.

        Interactive Tools typically are run exclusively with this method. Can poll for
        the interactive tool endpoint before returning, ensuring that the tool is reachable.

        Parameters
        ----------
        data_store: Datastore
            The data store to run this tool in.
        params: Parameters
            The input parameters for this tool.
        wait: bool
            Whether to wait for the interactive tool to start up before returning.
        max_tries: int
            Timeout for how long to poll for the interactive tool endpoint.
        check_url:
            Whether to check if the interactive tool endpoint is reachable before returning.

        Returns
        -------
        Optional[str]
            Will return None, if not waiting for interactive tool to startup with `wait` parameter. Will return
            the URL to the interactive tool otherwise.

        """
        self._job = Job(self.id, data_store)
        return self._job.run_interactive(params, wait=wait, max_tries=max_tries, check_url=check_url)

    def get_status(self) -> WorkState:
        """Returns the current status of the tool."""
        if self._job:
            return self._job.get_state().state
        else:
            return WorkState.NOT_STARTED

    def get_results(self) -> Optional[Outputs]:
        """Returns the results from running this tool.

        Throws an Exception if the tool has not finished yet. Will be
        overridden if this tool is run again.

        """
        if self._job:
            return self._job.get_results()
        return None

    def stop(self) -> None:
        """Stop the tool, but keep any existing results."""
        if self._job:
            self._job.cancel(check_results=True)

    def cancel(self) -> None:
        """Cancels the tool execution and gets rid of any results collected."""
        if self._job:
            self._job.cancel(check_results=False)

    def get_stdout(self) -> Optional[str]:
        """Get the current STDOUT for a tool. Will be overridden everytime this tool is run."""
        if self._job:
            return self._job.get_console_output()["stdout"]
        return None

    def get_stderr(self) -> Optional[str]:
        """Get the current STDERR for a tool. Will be overridden everytime this tool is run."""
        if self._job:
            return self._job.get_console_output()["stderr"]
        return None

    def get_url(self) -> Optional[str]:
        """Get the URL for this tool. If this is an interactive tool, then will return the endpoint to the tool."""
        if self._job:
            return self._job.get_url()
        return None

    def get_uid(self) -> Optional[str]:
        """Get the unique ID for this tool. Will only be available if Tool.run() has been successfully invoked."""
        if self._job:
            return self._job.id
        return None

    def assign_id(self, new_id: str, data_store: "Datastore") -> None:
        if self._job:
            raise Exception("Tool cannot be currently assigned an ID. Do not directly call this method.")
        self._job = Job(self.id, data_store)
        self._job.id = new_id
        self._job.status.state = WorkState.QUEUED


def stop_all_tools_in_store(data_store: "Datastore") -> None:
    """Stops all the tools from running in a particular store."""
    galaxy_instance = data_store.nova_connection.galaxy_instance
    jobs = galaxy_instance.jobs.get_jobs(history_id=data_store.history_id)
    for job in jobs:
        galaxy_instance.jobs.cancel_job(job["id"])
