from pathlib import Path
import pytest

from q.workflow.util.config import WorkflowConfig


@pytest.fixture
def research_workflow_config():
    path = Path(__file__).parent / "agent_config.json"
    return WorkflowConfig.model_validate_json(path.read_bytes())
