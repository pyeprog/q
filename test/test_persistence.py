from dataclasses import dataclass, field
from pathlib import Path

from pydantic_graph.graph import Graph
from pydantic_graph.nodes import BaseNode, GraphRunContext
import pytest
import pytest_asyncio

from q.workflow.persistence import FileLatestSnapshotPersistence


@dataclass
class State:
    countings: list[int] = field(default_factory=list)


@dataclass
class Counter(BaseNode[State]):
    async def run(self, ctx: GraphRunContext[State]) -> "Counter":
        if not ctx.state.countings:
            ctx.state.countings.append(0)
        else:
            ctx.state.countings.append(ctx.state.countings[-1] + 1)

        return Counter()


graph = Graph(nodes=(Counter,), state_type=State)


@pytest_asyncio.fixture
async def file_latest_snapshot_persistence():
    file_path = Path(__file__).parent / "latest_snapshot_persistence.json"
    persistence = FileLatestSnapshotPersistence(file_path)
    persistence.set_graph_types(graph)

    node = Counter()
    async with graph.iter(node, state=State(), persistence=persistence) as run:
        await run.next()
        await run.next()
        await run.next()

    yield persistence

    file_path.unlink()


@pytest.mark.asyncio
async def test_file_last_snapshot_persistence(file_latest_snapshot_persistence):
    persistence: FileLatestSnapshotPersistence = file_latest_snapshot_persistence

    snapshots = await persistence.load_all()
    assert len(snapshots) == 1

    if snapshot := await persistence.load_next():
        state = snapshot.state
    else:
        state = State()

    node = Counter()
    async with graph.iter(node, state=state, persistence=persistence) as run:
        await run.next()

    snapshots = await persistence.load_all()
    assert len(snapshots) == 1

    snapshot = await persistence.load_next()
    assert snapshot
    assert snapshot.state.countings == [0, 1, 2, 3]
