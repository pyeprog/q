from pydantic_graph.persistence import EndSnapshot, NodeSnapshot, RunEndT, StateT
from pydantic_graph.persistence.file import FileStatePersistence


PERSISTENCE_FILENAME = "history.json"


class FileLatestSnapshotPersistence(FileStatePersistence[StateT, RunEndT]):
    """It should only be used for simple graph with 2 nodes, a working node and a halt node.
    If multiple nodes are used and you'd like to load the next from persistence, it will return wrong node.

    Args:
        FileStatePersistence (_type_): _description_
    """

    def _save_sync(
        self,
        snapshots: list[NodeSnapshot[StateT, RunEndT] | EndSnapshot[StateT, RunEndT]],
    ) -> None:
        return super()._save_sync(snapshots[-1:])  # only save the last snapshot
