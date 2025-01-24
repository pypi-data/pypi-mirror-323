from __future__ import annotations

from dataclasses import dataclass
import json
from time import perf_counter
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel
from tokonomics import get_available_models
from tokonomics.toko_types import TokenUsage

from llmling_agent.common_types import ModelProtocol
from llmling_agent.log import get_logger
from llmling_agent.models.agents import ToolCallInfo
from llmling_agent.models.content import BaseContent, Content
from llmling_agent.models.messages import ChatMessage, TokenCost
from llmling_agent_providers.base import AgentProvider, ProviderResponse


if TYPE_CHECKING:
    from litellm import ChatCompletionMessageToolCall

    from llmling_agent.tools.base import ToolInfo


logger = get_logger(__name__)


class LiteLLMModel:
    """Compatible model class for LiteLLM."""

    def __init__(self, model_name: str):
        self._name = model_name

    def name(self) -> str:
        return self._name.replace(":", "/")


@dataclass
class LiteLLMRunContext:
    """Simple run context for LiteLLM provider."""

    message_id: str
    model: LiteLLMModel
    prompt: str
    deps: Any


class LiteLLMProvider(AgentProvider[Any]):
    """Provider using LiteLLM for model-agnostic completions."""

    def __init__(
        self,
        name: str,
        model: str | ModelProtocol | None = None,
        *,
        debug: bool = False,
        retries: int = 1,
    ):
        super().__init__(name=name, debug=debug)
        self._model = model
        self.num_retries = retries

    async def get_model_names(self) -> list[str]:
        """Get list of all known model names."""
        return await get_available_models()

    async def handle_tool_call(
        self,
        tool_call: ChatCompletionMessageToolCall,
        tool: ToolInfo,
        message_id: str,
    ) -> tuple[ToolCallInfo, dict]:
        """Handle a single tool call properly."""
        function_args = json.loads(tool_call.function.arguments)
        start_time = perf_counter()
        result = await tool.execute(**function_args)
        info = ToolCallInfo(
            tool_name=tool.name,
            agent_name=self.name,
            args=function_args,
            result=result,
            tool_call_id=tool_call.id,
            timing=perf_counter() - start_time,
            message_id=message_id,
        )
        self.tool_used.emit(info)
        message = {
            "tool_call_id": tool_call.id,
            "role": "tool",
            "name": tool.name,
            "content": result,
        }

        return info, message

    async def generate_response(
        self,
        *prompts: str | Content,
        message_id: str,
        result_type: type[Any] | None = None,
        model: ModelProtocol | str | None = None,
        store_history: bool = True,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> ProviderResponse:
        """Generate response using LiteLLM."""
        from litellm import Choices, acompletion
        from litellm.files.main import ModelResponse

        model_name = self._get_model_name(model)
        complete_history = self.conversation.get_history()
        try:
            # Create messages list from history and new prompt
            messages: list[dict[str, Any]] = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            if store_history:
                for msg in complete_history:
                    messages.extend(self._convert_message_to_chat(msg))

            # Convert new prompts to message content
            content_parts: list[dict[str, Any]] = []
            for p in prompts:
                match p:
                    case str():
                        content_parts.append({"type": "text", "text": p})
                    case BaseContent():
                        content_parts.append(p.to_openai_format())
            # Add the multi-modal content as user message
            messages.append({"role": "user", "content": content_parts})

            schemas = [t.get_schema() for t in self.tool_manager.get_tools("enabled")]
            # Get completion
            response = await acompletion(
                stream=False,
                model=model_name,
                messages=messages,
                response_format=result_type
                if result_type and issubclass(result_type, BaseModel)
                else None,
                num_retries=self.num_retries,
                tools=schemas or None,
                tool_choice=self.get_tool_choice() if schemas else None,
                **kwargs,
            )
            assert isinstance(response, ModelResponse)
            assert isinstance(response.choices[0], Choices)
            calls: list[ToolCallInfo] = []
            for tool_call in response.choices[0].message.tool_calls or []:
                function_name = tool_call.function.name
                if not function_name:
                    continue
                tool = self.tool_manager.get(function_name)
                info, message = await self.handle_tool_call(tool_call, tool, message_id)
                calls.append(info)
                messages.append(message)
            # Extract content
            content = response.choices[0].message.content
            if content and result_type and issubclass(result_type, BaseModel):
                # Parse JSON string into the requested model
                content = result_type.model_validate_json(content)
            # Create tokonomics usage
            usage = TokenUsage(
                total_tokens=response.usage.prompt_tokens,  # type: ignore
                request_tokens=response.usage.prompt_tokens,  # type: ignore
                response_tokens=response.usage.completion_tokens,  # type: ignore
            )
            cost_and_usage = TokenCost(
                token_usage=usage,
                total_cost=response.usage.cost,  # type: ignore
            )
            # Store in history if requested
            if store_history:
                request_msgs = [ChatMessage(role="user", content=str(p)) for p in prompts]
                response_msg = ChatMessage(role="assistant", content=content)
                self.conversation.add_chat_messages([*request_msgs, response_msg])

            return ProviderResponse(
                content=content,
                tool_calls=calls,
                model_name=model_name,
                cost_and_usage=cost_and_usage,
            )

        except Exception as e:
            logger.exception("LiteLLM completion failed")
            error_msg = f"LiteLLM completion failed: {e}"
            raise RuntimeError(error_msg) from e

    def _get_model_name(self, override: ModelProtocol | str | None = None) -> str:
        """Get effective model name."""
        if isinstance(override, ModelProtocol):
            return override.name()
        if isinstance(override, str):
            return override.replace(":", "/")
        if isinstance(self._model, ModelProtocol):
            return self._model.name()
        if self._model:
            return self._model.replace(":", "/")
        return "openai/gpt-4o-mini"

    def get_tool_choice(self) -> str:
        match self.tool_manager.tool_choice:
            case True:
                return "auto"
            case False:
                return "none"
            case str():
                return self.tool_manager.tool_choice
            case list():
                return "auto"

    def _convert_message_to_chat(self, message: Any) -> list[dict[str, str]]:
        """Convert message to chat format."""
        # This is a basic implementation - would need to properly handle
        # different message types and parts
        return [{"role": "user", "content": str(message)}]

    # async def stream_response(
    #     self,
    #     *prompts: str | Content,
    #     message_id: str,
    #     *,
    #     result_type: type[Any] | None = None,
    #     model: LiteLLMModel | str | None = None,
    #     store_history: bool = True,
    #     system_prompt: str | None = None,

    #     **kwargs: Any,
    # ) -> AbstractAsyncContextManager[StreamingResponseProtocol]:
    #     """Stream response from LiteLLM.

    #     Not implemented yet - would need to handle streaming responses.
    #     """
    #     msg = "Streaming not yet supported"
    #     raise NotImplementedError(msg)


if __name__ == "__main__":
    import logging

    from llmling_agent import Agent

    logging.basicConfig(level=logging.INFO)

    # Create agent with LiteLLM provider
    agent = Agent[Any](provider="litellm", model="openai/gpt-3.5-turbo", name="test")

    # Use run_sync for simple testing
    response = agent.run_sync("Tell me a short joke about Python programming.")

    print(f"\nResponse from {agent.model_name}:")
    print(f"Content: {response.content}")
    if response.cost_info:
        print(f"Tokens: {response.cost_info.token_usage}")
        print(f"Cost: ${response.cost_info.total_cost:.4f}")
