"""DataStore is used to configure Galaxy to group outputs of a tool together."""

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .nova import NovaConnection  # Only imports for type checking

from .tool import Tool


class Datastore:
    """Groups tool outputs together.

    The constructor is not intended for external use. Use nova.galaxy.Nova.create_data_store() instead.
    """

    def __init__(self, name: str, nova_connection: "NovaConnection", history_id: str) -> None:
        self.name = name
        self.nova_connection = nova_connection
        self.history_id = history_id
        self.persist_store = False

    def persist(self) -> None:
        """Persist this store even after the nova connection is closed.

        Should be used carefully as tools will continue to run after even if this object is garbage collected.
        Use recover_tools() to with the same data store name to retrieve all running tools again.
        """
        self.persist_store = True

    def recover_tools(self) -> List[Tool]:
        """Recovers all running tools in this data_store.

        Mainly used to recover all the running tools inside of this data store or any past persisted data stores that
        used the same name. Can also be used to simply get a list of all running tools in a store as well.
        """
        history_contents = self.nova_connection.galaxy_instance.histories.show_history(
            self.history_id, contents=True, deleted=False, details="all"
        )
        tools = []
        for dataset in history_contents:
            job_id = dataset.get("creating_job", None)
            if job_id:
                tool_id = self.nova_connection.galaxy_instance.jobs.show_job(job_id)["tool_id"]
                t = Tool(tool_id)
                t.assign_id(job_id, self)
                t.get_url()
                t.get_status()
                tools.append(t)
        return tools
