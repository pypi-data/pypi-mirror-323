# @Author: Bi Ying
# @Date:   2024-07-26 14:48:55
import random
from abc import ABC, abstractmethod
from functools import cached_property
from typing import Generator, AsyncGenerator, Any, overload, Literal, Iterable

import httpx
from openai import OpenAI, AsyncOpenAI, AzureOpenAI, AsyncAzureOpenAI
from anthropic import (
    Anthropic,
    AsyncAnthropic,
    AnthropicVertex,
    AsyncAnthropicVertex,
    AnthropicBedrock,
    AsyncAnthropicBedrock,
)

from ..settings import settings
from ..types import defaults as defs
from ..types.enums import ContextLengthControlType, BackendType
from ..types.llm_parameters import (
    NotGiven,
    NOT_GIVEN,
    ToolParam,
    ToolChoice,
    EndpointSetting,
    ChatCompletionMessage,
    ChatCompletionDeltaMessage,
    ChatCompletionStreamOptionsParam,
)


class BaseChatClient(ABC):
    DEFAULT_MODEL: str
    BACKEND_NAME: BackendType

    def __init__(
        self,
        model: str = "",
        stream: bool = False,
        temperature: float | None | NotGiven = NOT_GIVEN,
        context_length_control: ContextLengthControlType = defs.CONTEXT_LENGTH_CONTROL,
        random_endpoint: bool = True,
        endpoint_id: str = "",
        http_client: httpx.Client | None = None,
        backend_name: str | None = None,
    ):
        self.model = model or self.DEFAULT_MODEL
        self.stream = stream
        self.temperature = temperature
        self.context_length_control = context_length_control
        self.random_endpoint = random_endpoint
        self.endpoint_id = endpoint_id
        self.http_client = http_client

        if backend_name is not None:
            self.BACKEND_NAME = BackendType(backend_name)

        self.backend_settings = settings.get_backend(self.BACKEND_NAME)

        if endpoint_id:
            self.endpoint_id = endpoint_id
            self.random_endpoint = False
            self.endpoint = settings.get_endpoint(self.endpoint_id)

    def set_model_id_by_endpoint_id(self, endpoint_id: str):
        for endpoint_option in self.backend_settings.models[self.model].endpoints:
            if isinstance(endpoint_option, dict) and endpoint_id == endpoint_option["endpoint_id"]:
                self.model_id = endpoint_option["model_id"]
                break
        return self.model_id

    def _set_endpoint(self):
        if self.endpoint is None:
            if self.random_endpoint:
                self.random_endpoint = True
                endpoint = random.choice(self.backend_settings.models[self.model].endpoints)
                if isinstance(endpoint, dict):
                    self.endpoint_id = endpoint["endpoint_id"]
                    self.model_id = endpoint["model_id"]
                else:
                    self.endpoint_id = endpoint
                self.endpoint = settings.get_endpoint(self.endpoint_id)
            else:
                self.endpoint = settings.get_endpoint(self.endpoint_id)
                self.set_model_id_by_endpoint_id(self.endpoint_id)
        elif isinstance(self.endpoint, EndpointSetting):
            self.endpoint_id = self.endpoint.id
            self.set_model_id_by_endpoint_id(self.endpoint_id)
        else:
            raise ValueError("Invalid endpoint")

        return self.endpoint, self.model_id

    @cached_property
    @abstractmethod
    def raw_client(
        self,
    ) -> OpenAI | AzureOpenAI | Anthropic | AnthropicVertex | AnthropicBedrock | httpx.Client | None:
        pass

    @overload
    @abstractmethod
    def create_completion(
        self,
        *,
        messages: list,
        model: str | None = None,
        stream: Literal[False] = False,
        temperature: float | None | NotGiven = NOT_GIVEN,
        max_tokens: int | None = None,
        tools: Iterable[ToolParam] | NotGiven = NOT_GIVEN,
        tool_choice: ToolChoice | NotGiven = NOT_GIVEN,
        response_format: dict | None = None,
        stream_options: ChatCompletionStreamOptionsParam | None = None,
        top_p: float | NotGiven | None = NOT_GIVEN,
        skip_cutoff: bool = False,
        **kwargs,
    ) -> ChatCompletionMessage:
        pass

    @overload
    @abstractmethod
    def create_completion(
        self,
        *,
        messages: list,
        model: str | None = None,
        stream: Literal[True],
        temperature: float | None | NotGiven = NOT_GIVEN,
        max_tokens: int | None = None,
        tools: Iterable[ToolParam] | NotGiven = NOT_GIVEN,
        tool_choice: ToolChoice | NotGiven = NOT_GIVEN,
        response_format: dict | None = None,
        stream_options: ChatCompletionStreamOptionsParam | None = None,
        top_p: float | NotGiven | None = NOT_GIVEN,
        skip_cutoff: bool = False,
        **kwargs,
    ) -> Generator[ChatCompletionDeltaMessage, Any, None]:
        pass

    @overload
    @abstractmethod
    def create_completion(
        self,
        *,
        messages: list,
        model: str | None = None,
        stream: bool,
        temperature: float | None | NotGiven = NOT_GIVEN,
        max_tokens: int | None = None,
        tools: Iterable[ToolParam] | NotGiven = NOT_GIVEN,
        tool_choice: ToolChoice | NotGiven = NOT_GIVEN,
        response_format: dict | None = None,
        stream_options: ChatCompletionStreamOptionsParam | None = None,
        top_p: float | NotGiven | None = NOT_GIVEN,
        skip_cutoff: bool = False,
        **kwargs,
    ) -> ChatCompletionMessage | Generator[ChatCompletionDeltaMessage, Any, None]:
        pass

    @abstractmethod
    def create_completion(
        self,
        *,
        messages: list,
        model: str | None = None,
        stream: Literal[False] | Literal[True] = False,
        temperature: float | None | NotGiven = NOT_GIVEN,
        max_tokens: int | None = None,
        tools: Iterable[ToolParam] | NotGiven = NOT_GIVEN,
        tool_choice: ToolChoice | NotGiven = NOT_GIVEN,
        response_format: dict | None = None,
        stream_options: ChatCompletionStreamOptionsParam | None = None,
        top_p: float | NotGiven | None = NOT_GIVEN,
        skip_cutoff: bool = False,
        **kwargs,
    ) -> ChatCompletionMessage | Generator[ChatCompletionDeltaMessage, Any, None]:
        pass

    def create_stream(
        self,
        *,
        messages: list,
        model: str | None = None,
        temperature: float | None | NotGiven = NOT_GIVEN,
        max_tokens: int | None = None,
        tools: Iterable[ToolParam] | NotGiven = NOT_GIVEN,
        tool_choice: ToolChoice | NotGiven = NOT_GIVEN,
        response_format: dict | None = None,
        stream_options: ChatCompletionStreamOptionsParam | None = None,
        top_p: float | NotGiven | None = NOT_GIVEN,
        **kwargs,
    ) -> Generator[ChatCompletionDeltaMessage, Any, None]:
        return self.create_completion(
            messages=messages,
            model=model,
            stream=True,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=tools,
            tool_choice=tool_choice,
            response_format=response_format,
            stream_options=stream_options,
            top_p=top_p,
            **kwargs,
        )


class BaseAsyncChatClient(ABC):
    DEFAULT_MODEL: str
    BACKEND_NAME: BackendType

    def __init__(
        self,
        model: str = "",
        stream: bool = False,
        temperature: float | None | NotGiven = NOT_GIVEN,
        context_length_control: ContextLengthControlType = defs.CONTEXT_LENGTH_CONTROL,
        random_endpoint: bool = True,
        endpoint_id: str = "",
        http_client: httpx.AsyncClient | None = None,
        backend_name: str | None = None,
    ):
        self.model = model or self.DEFAULT_MODEL
        self.stream = stream
        self.temperature = temperature
        self.context_length_control = context_length_control
        self.random_endpoint = random_endpoint
        self.endpoint_id = endpoint_id
        self.http_client = http_client

        if backend_name is not None:
            self.BACKEND_NAME = BackendType(backend_name)

        self.backend_settings = settings.get_backend(self.BACKEND_NAME)

        if endpoint_id:
            self.endpoint_id = endpoint_id
            self.random_endpoint = False
            self.endpoint = settings.get_endpoint(self.endpoint_id)

    def set_model_id_by_endpoint_id(self, endpoint_id: str):
        for endpoint_option in self.backend_settings.models[self.model].endpoints:
            if isinstance(endpoint_option, dict) and endpoint_id == endpoint_option["endpoint_id"]:
                self.model_id = endpoint_option["model_id"]
                break
        return self.model_id

    def _set_endpoint(self):
        if self.endpoint is None:
            if self.random_endpoint:
                self.random_endpoint = True
                endpoint = random.choice(self.backend_settings.models[self.model].endpoints)
                if isinstance(endpoint, dict):
                    self.endpoint_id = endpoint["endpoint_id"]
                    self.model_id = endpoint["model_id"]
                else:
                    self.endpoint_id = endpoint
                self.endpoint = settings.get_endpoint(self.endpoint_id)
            else:
                self.endpoint = settings.get_endpoint(self.endpoint_id)
                self.set_model_id_by_endpoint_id(self.endpoint_id)
        elif isinstance(self.endpoint, EndpointSetting):
            self.endpoint_id = self.endpoint.id
            self.set_model_id_by_endpoint_id(self.endpoint_id)
        else:
            raise ValueError("Invalid endpoint")

        return self.endpoint, self.model_id

    @cached_property
    @abstractmethod
    def raw_client(
        self,
    ) -> (
        AsyncOpenAI
        | AsyncAzureOpenAI
        | AsyncAnthropic
        | AsyncAnthropicVertex
        | AsyncAnthropicBedrock
        | httpx.AsyncClient
        | None
    ):
        pass

    @overload
    @abstractmethod
    async def create_completion(
        self,
        *,
        messages: list,
        model: str | None = None,
        stream: Literal[False] = False,
        temperature: float | None | NotGiven = NOT_GIVEN,
        max_tokens: int | None = None,
        tools: list | NotGiven = NOT_GIVEN,
        tool_choice: ToolChoice | NotGiven = NOT_GIVEN,
        response_format: dict | None = None,
        stream_options: ChatCompletionStreamOptionsParam | None = None,
        top_p: float | NotGiven | None = NOT_GIVEN,
        skip_cutoff: bool = False,
        **kwargs,
    ) -> ChatCompletionMessage:
        pass

    @overload
    @abstractmethod
    async def create_completion(
        self,
        *,
        messages: list,
        model: str | None = None,
        stream: Literal[True],
        temperature: float | None | NotGiven = NOT_GIVEN,
        max_tokens: int | None = None,
        tools: list | NotGiven = NOT_GIVEN,
        tool_choice: ToolChoice | NotGiven = NOT_GIVEN,
        response_format: dict | None = None,
        stream_options: ChatCompletionStreamOptionsParam | None = None,
        top_p: float | NotGiven | None = NOT_GIVEN,
        skip_cutoff: bool = False,
        **kwargs,
    ) -> AsyncGenerator[ChatCompletionDeltaMessage, None]:
        pass

    @overload
    @abstractmethod
    async def create_completion(
        self,
        *,
        messages: list,
        model: str | None = None,
        stream: bool,
        temperature: float | None | NotGiven = NOT_GIVEN,
        max_tokens: int | None = None,
        tools: list | NotGiven = NOT_GIVEN,
        tool_choice: ToolChoice | NotGiven = NOT_GIVEN,
        response_format: dict | None = None,
        stream_options: ChatCompletionStreamOptionsParam | None = None,
        top_p: float | NotGiven | None = NOT_GIVEN,
        skip_cutoff: bool = False,
        **kwargs,
    ) -> ChatCompletionMessage | AsyncGenerator[ChatCompletionDeltaMessage, None]:
        pass

    @abstractmethod
    async def create_completion(
        self,
        *,
        messages: list,
        model: str | None = None,
        stream: Literal[False] | Literal[True] = False,
        temperature: float | None | NotGiven = NOT_GIVEN,
        max_tokens: int | None = None,
        tools: list | NotGiven = NOT_GIVEN,
        tool_choice: ToolChoice | NotGiven = NOT_GIVEN,
        response_format: dict | None = None,
        stream_options: ChatCompletionStreamOptionsParam | None = None,
        top_p: float | NotGiven | None = NOT_GIVEN,
        skip_cutoff: bool = False,
        **kwargs,
    ) -> ChatCompletionMessage | AsyncGenerator[ChatCompletionDeltaMessage, None]:
        pass

    async def create_stream(
        self,
        *,
        messages: list,
        model: str | None = None,
        temperature: float | None | NotGiven = NOT_GIVEN,
        max_tokens: int | None = None,
        tools: list | NotGiven = NOT_GIVEN,
        tool_choice: ToolChoice | NotGiven = NOT_GIVEN,
        response_format: dict | None = None,
        stream_options: ChatCompletionStreamOptionsParam | None = None,
        top_p: float | NotGiven | None = NOT_GIVEN,
        **kwargs,
    ) -> AsyncGenerator[ChatCompletionDeltaMessage, None]:
        return await self.create_completion(
            messages=messages,
            model=model,
            stream=True,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=tools,
            tool_choice=tool_choice,
            response_format=response_format,
            stream_options=stream_options,
            top_p=top_p,
            **kwargs,
        )
