from dataclasses import dataclass
from functools import lru_cache
from pydantic import BaseModel
from typing import (
    AsyncGenerator,
    Iterator,
    Literal,
    Protocol,
    Type,
    TypeVar,
)
from openai import AsyncOpenAI, OpenAI, Stream
from openai.types.chat import ChatCompletion, ChatCompletionChunk
import httpx
import anthropic
from anthropic.types import Message as AnthropicMessage

from texty.settings import settings


OPENAI_TEMPERATURE = 0.7

import logging

logger = logging.getLogger(__name__)


def get_client(model: Literal["small", "large"]) -> "LLMModel":
    resolved = (
        settings.llm_model_small if model == "small" else settings.llm_model_large
    )

    split = resolved.split("/", 1)

    if len(split) == 1 or split[0] not in ["anthropic", "openai"]:
        raise ValueError(
            f"Invalid model '{resolved}': Model must be qualified with a supported provider, for example anthropic/claude-sonnet-3.5"
        )

    if split[0] == "anthropic":
        return AnthropicModel(ModelConfig(model=split[1]))
    else:
        return OpenAIModel(ModelConfig(model=split[1]))


T = TypeVar("T", bound=BaseModel)


class LLMModel(Protocol):
    async def text(self, prompt: str) -> str: ...
    async def stream(self, prompt: str) -> Iterator[str]: ...
    async def json(self, prompt: str, schema: Type[T]) -> T: ...


@dataclass
class ModelConfig:
    model: str
    temperature: float = 0.7


class OpenAIModel(LLMModel):
    def __init__(self, config: ModelConfig):
        self.client = get_openai()
        self.config = config

    async def text(self, prompt: str) -> str:
        response: ChatCompletion = await self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=self.config.model,
            temperature=self.config.temperature,
        )
        return response.choices[0].message.content

    async def stream(self, prompt: str) -> AsyncGenerator[str, None]:
        response: Stream[ChatCompletionChunk] = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            stream=True,
            model=self.config.model,
            temperature=self.config.temperature,
        )
        async for chunk in response:
            if chunk.choices[0].finish_reason is not None:
                break
            else:
                yield chunk.choices[0].delta.content

    async def json(self, prompt: str, schema: Type[T]) -> T:
        kwargs = {}
        if settings.llama_cpp_json_schema:
            kwargs["extra_body"] = {"json_schema": schema.model_json_schema()}
        elif settings.openai_tool_mode:
            kwargs["tools"] = [
                {
                    "type": "function",
                    "function": {
                        "name": "respond",
                        "parameters": schema.model_json_schema(),
                    },
                }
            ]
            kwargs["tool_choice"] = "required"
        else:
            kwargs["response_format"] = {"type": "json_object"}

        response: ChatCompletion = await self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=self.config.model,
            temperature=self.config.temperature,
            **kwargs,
        )

        if settings.openai_tool_mode:
            txt = response.choices[0].message.tool_calls[0].function.arguments
        else:
            txt = response.choices[0].message.content

        try:
            return schema.model_validate_json(txt)
        except Exception as e:
            print("could not parse", txt)
            raise


class AnthropicModel(LLMModel):
    def __init__(self, config: ModelConfig):
        self.client = get_anthropic()
        self.config = config

    async def text(self, prompt: str) -> str:
        response: AnthropicMessage = await self.client.messages.create(
            messages=[{"content": prompt, "role": "user"}],
            model=self.config.model,
            temperature=self.config.temperature,
            max_tokens=4096,
        )
        return response.content[0].text

    async def stream(self, prompt: str) -> AsyncGenerator[str, None]:
        async with self.client.messages.stream(
            messages=[{"content": prompt, "role": "user"}],
            model=self.config.model,
            temperature=self.config.temperature,
            max_tokens=4096,
        ) as stream:
            stream: anthropic.MessageStream = stream
            async for text in stream.text_stream:
                yield text

    async def json(self, prompt: str, schema: Type[T]) -> T:
        response: AnthropicMessage = await self.client.messages.create(
            messages=[{"content": prompt, "role": "user"}],
            tools=[
                {
                    "input_schema": schema.model_json_schema(),
                    "name": "respond",
                }
            ],
            tool_choice={"name": "respond", "type": "tool"},
            model=self.config.model,
            temperature=self.config.temperature,
            max_tokens=4096,
        )

        return schema.model_validate(response.content[0].input)


@lru_cache(maxsize=None)
def get_openai() -> OpenAI:
    client = httpx.Client()
    return AsyncOpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
        http_client=client,
    )


@lru_cache(maxsize=None)
def get_anthropic() -> anthropic.Client:
    return anthropic.AsyncClient(api_key=settings.anthropic_api_key)
