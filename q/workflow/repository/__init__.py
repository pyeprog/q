from q.workflow.base_workflow import BaseWorkflow
from q.workflow.repository.deep_research import DeepResearchWorkflow
from q.workflow.repository.default import ChatWorkflow
from q.workflow.repository.web_search import SearchWorkflow


WORKFLOW_MAP: dict[str, type[BaseWorkflow]] = {
    "research": DeepResearchWorkflow,
    "default": ChatWorkflow,
    "search": SearchWorkflow,
}
