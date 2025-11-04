from q.workflow.base_workflow import BaseWorkflow
from q.workflow.repository.deep_research import DeepResearchWorkflow
from q.workflow.repository.default import ChatWorkflow


WORKFLOW_MAP: dict[str, type[BaseWorkflow]] = {
    "research": DeepResearchWorkflow,
    "default": ChatWorkflow,
}
