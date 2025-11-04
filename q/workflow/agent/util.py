import inspect
from pathlib import Path
from typing import Callable
from dotenv.main import load_dotenv
from pydantic_ai.messages import (
    FinalResultEvent,
    FunctionToolCallEvent,
    FunctionToolResultEvent,
    ModelResponse,
    PartDeltaEvent,
    PartStartEvent,
    TextPart,
)
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openrouter import OpenRouterProvider
from more_itertools.more import first

AgentEvent = PartStartEvent | PartDeltaEvent | FinalResultEvent | FunctionToolCallEvent | FunctionToolResultEvent


def agent_event_stream_handler(event_handlers: list[Callable]):
    async def handler(ctx, stream):
        async for event in stream:
            for handler in event_handlers:
                if (parameter := first(inspect.signature(handler).parameters.values(), None)) and isinstance(
                    event, parameter.annotation
                ):
                    handler(event)

    return handler


def open_router_model(model_name: str, env_path: Path | None = None) -> OpenAIChatModel:
    env_path = env_path or Path.cwd()
    dotenv_file = env_path / ".env"
    assert dotenv_file.exists(), f".env file not found in {env_path}"
    assert load_dotenv(dotenv_file)

    return OpenAIChatModel(model_name=model_name, provider=OpenRouterProvider())


def model_response(text_list: list[str]) -> ModelResponse:
    return ModelResponse(parts=[TextPart(text) for text in text_list])
