from itertools import chain
from pathlib import Path

from pydantic.fields import Field
from pydantic.main import BaseModel
from pydantic_graph.graph import Graph
from pydantic_graph.persistence.file import BaseStatePersistence, FileStatePersistence
from pydantic_graph.persistence import Snapshot

from q.workflow.agent.config import AgentConfig
from q.workflow.base_workflow import BaseWorkflow
from q.workflow.persistence import PERSISTENCE_FILENAME
from q.workflow.util.typing import AgentConfigMap

CONFIG_FILENAME = "agent_config.json"


class WorkflowConfig(BaseModel):
    """collector for config passing through cli"""

    workflow_name: str = "placeholder"
    agent_config_map: AgentConfigMap = Field(default_factory=dict)

    def get_agent_config(self, agent_name: str) -> AgentConfig:
        return self.agent_config_map[agent_name]

    def tools_names(self) -> set[str]:
        return set(chain.from_iterable([config.tool_names for config in self.agent_config_map.values()]))


def load_config(dir_: str | Path = ".") -> WorkflowConfig:
    path = Path(dir_) / CONFIG_FILENAME
    if not path.exists():
        raise FileNotFoundError(f"Config file {path} not found at {str(Path(dir_).absolute())}.")

    return WorkflowConfig.model_validate_json(path.read_bytes())


def save_config(config: WorkflowConfig, dir_: str | Path = ".", append: bool = True):
    path = Path(dir_) / CONFIG_FILENAME

    origin_config = WorkflowConfig()
    if append and path.exists():
        origin_config = WorkflowConfig.model_validate_json(path.read_bytes())

    config.agent_config_map.update(origin_config.agent_config_map)

    path.write_text(config.model_dump_json())


class LocalConfigLoader:
    def __init__(self, directory: str | Path, workflow_map: dict[str, type[BaseWorkflow]]) -> None:
        self._dir: Path = Path(directory)
        assert self._dir.exists() and self._dir.is_dir(), "directory must exist and be a directory"
        self._config_file = self._dir / CONFIG_FILENAME
        assert self._config_file.exists() and self._config_file.is_file(), "config file must exist and be a file"

        self._workflow_map = workflow_map

    @property
    def workflow_config(self) -> WorkflowConfig:
        return load_config(self._dir)

    @property
    def graph(self) -> Graph:
        return self._workflow_map[self.workflow_config.workflow_name].graph()  # type: ignore

    @property
    def state_type(self):
        return self.graph._state_type

    @property
    def persistence(self) -> BaseStatePersistence | None:
        history_file = self._dir / PERSISTENCE_FILENAME
        if not (history_file.exists() and history_file.is_file()):
            return None

        persistence = FileStatePersistence(history_file)
        persistence.set_graph_types(self.graph)
        return persistence

    async def snapshots(self) -> list[Snapshot]:
        if not self.persistence:
            return []

        return await self.persistence.load_all()
