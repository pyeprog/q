from q.workflow.base_workflow import BaseWorkflow
from q.workflow.repository.default import ChatWorkflow
from q.workflow.repository.deep_research import DeepResearchWorkflow


WORKFLOW_MAP: dict[str, type[BaseWorkflow]] = {
    "default": ChatWorkflow,
    "research": DeepResearchWorkflow,
}
