import inspect
import json
from enum import Enum
from typing import Any, Literal

import httpx
from pydantic import BaseModel, Field

from ironhide.settings import settings


class PropertyDefinition(BaseModel):
    type: str
    description: str


class ParametersDefinition(BaseModel):
    type: str = "object"
    properties: dict[str, PropertyDefinition]
    required: list[str]
    additionalProperties: bool = False


class FunctionDefinition(BaseModel):
    name: str
    description: str
    parameters: ParametersDefinition
    strict: bool = True


class ToolDefinition(BaseModel):
    type: str = "function"
    function: FunctionDefinition


class Headers(BaseModel):
    content_type: str = Field(
        alias="Content-Type",
        default="application/json",
    )
    authorization: str = Field(
        alias="Authorization",
        default=f"Bearer {settings.openai_api_key}",
    )


class Role(str, Enum):
    system = "system"
    assistant = "assistant"
    user = "user"
    tool = "tool"


class PromptTokensDetails(BaseModel):
    cached_tokens: int
    audio_tokens: int


class CompletionTokensDetails(BaseModel):
    reasoning_tokens: int
    audio_tokens: int
    accepted_prediction_tokens: int
    rejected_prediction_tokens: int


class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    prompt_tokens_details: PromptTokensDetails
    completion_tokens_details: CompletionTokensDetails


class ToolFunction(BaseModel):
    name: str
    arguments: str


class ToolCall(BaseModel):
    id: str
    type: Literal["function"]
    function: ToolFunction


class Message(BaseModel):
    role: Role
    content: str | None = None
    tool_calls: list[ToolCall] | None = None
    tool_call_id: str | None = None
    refusal: str | None = None
    model_config = {"use_enum_values": True}


class Choice(BaseModel):
    index: int
    message: Message
    logprobs: dict[str, Any] | None = None
    finish_reason: str


class ChatCompletion(BaseModel):
    id: str
    object: Literal["chat.completion"]
    created: int
    model: str
    choices: list[Choice]
    usage: Usage
    service_tier: str
    system_fingerprint: str


class JsonSchema(BaseModel):
    name: str
    schema_: dict[str, Any] = Field(alias="schema")
    strict: bool = True


class ResponseFormat(BaseModel):
    type: str = "json_schema"
    json_schema: JsonSchema


class Data(BaseModel):
    model: str
    messages: list[Message]
    response_format: ResponseFormat | None = None
    tools: list[ToolDefinition] | None = None


class BaseAgent:
    model: str = ""
    system_message: str | None = None
    response_format: type[BaseModel] | None = None

    def __init__(self) -> None:
        if self.__doc__ is not None:
            self.system_message: str = self.__doc__.strip()
        else:
            self.system_message = getattr(type(self), "system_message", None)
        self.model = getattr(type(self), "model", "")
        self.response_format = getattr(type(self), "response_format", None)
        messages: list[Message] = []
        if self.system_message:
            messages.append(Message(role=Role.system, content=self.system_message))
        self.dict_tool: dict[str, Any] = {}
        self.data = Data(
            model=self.model,
            messages=messages,
            response_format=self._make_response_format_section(),
            tools=self._generate_tools(),
        )
        self.client = httpx.AsyncClient()
        self.headers = Headers()

    def _make_response_format_section(self) -> ResponseFormat | None:
        if self.response_format is None:
            return None
        schema = self.response_format.model_json_schema()
        schema["additionalProperties"] = False
        return ResponseFormat(
            json_schema=JsonSchema(
                name=schema["title"],
                schema=schema,
            ),
        )

    def _generate_tools(self) -> list[ToolDefinition]:
        tools = []
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if name.startswith("_") or name == "chat":
                continue
            docstring = inspect.getdoc(method) or ""
            sig = inspect.signature(method)
            properties: dict[str, PropertyDefinition] = {}
            required = []
            for param_name, param in sig.parameters.items():
                if param_name == "self":
                    continue
                annotation = param.annotation
                param_desc = ""
                if getattr(annotation, "__metadata__", None):
                    param_desc = annotation.__metadata__[0]
                    annotation = annotation.__args__[0]
                json_type = "string"
                if annotation in {int, float}:
                    json_type = "number"
                elif annotation is bool:
                    json_type = "boolean"
                if param.default is param.empty:
                    required.append(param_name)
                properties[param_name] = PropertyDefinition(
                    type=json_type,
                    description=param_desc,
                )

            tool_definition = ToolDefinition(
                function=FunctionDefinition(
                    name=name,
                    description=docstring.strip(),
                    parameters=ParametersDefinition(
                        properties=properties,
                        required=required,
                    ),
                ),
            )
            tools.append(tool_definition)
            self.dict_tool[name] = method
        return tools

    async def _call_function(self, name: str, args: dict[str, Any]) -> Any:
        selected_tool = self.dict_tool[name]
        if inspect.iscoroutinefunction(selected_tool):
            return await selected_tool(**args)
        return selected_tool(**args)

    async def _api_call(self) -> ChatCompletion:
        response = await self.client.post(
            "https://api.openai.com/v1/chat/completions",
            headers=self.headers.model_dump(by_alias=True),
            json=self.data.model_dump(by_alias=True),
            timeout=30.0,
        )
        return ChatCompletion(**response.json())

    async def chat(self, content: str) -> str:
        self.data.messages.append(Message(role=Role.user, content=content))
        completion = await self._api_call()
        self.data.messages.append(completion.choices[0].message)
        tool_calls = completion.choices[0].message.tool_calls
        while tool_calls:
            for tool_call in tool_calls:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                id_ = tool_call.id
                result = await self._call_function(name, args)
                self.data.messages.append(
                    Message(role=Role.tool, content=str(result), tool_call_id=id_),
                )
            completion = await self._api_call()
            self.data.messages.append(completion.choices[0].message)
            tool_calls = completion.choices[0].message.tool_calls
        return completion.choices[0].message.content or ""
