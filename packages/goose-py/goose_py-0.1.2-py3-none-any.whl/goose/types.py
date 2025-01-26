import base64
from datetime import datetime
from enum import StrEnum
from typing import ClassVar, Literal, NotRequired, TypedDict

from pydantic import BaseModel, computed_field


class GeminiModel(StrEnum):
    EXP = "gemini/gemini-exp-1121"
    PRO = "gemini/gemini-1.5-pro"
    FLASH = "gemini/gemini-1.5-flash"
    FLASH_8B = "gemini/gemini-1.5-flash-8b"


class UserMediaContentType(StrEnum):
    # images
    JPEG = "image/jpeg"
    PNG = "image/png"
    WEBP = "image/webp"

    # audio
    MP3 = "audio/mpeg"
    WAV = "audio/wav"

    # files
    PDF = "application/pdf"


class LLMTextMessagePart(TypedDict):
    type: Literal["text"]
    text: str


class LLMMediaMessagePart(TypedDict):
    type: Literal["image_url"]
    image_url: str


class CacheControl(TypedDict):
    type: Literal["ephemeral"]


class LLMMessage(TypedDict):
    role: Literal["user", "assistant", "system"]
    content: list[LLMTextMessagePart | LLMMediaMessagePart]
    cache_control: NotRequired[CacheControl]


class TextMessagePart(BaseModel):
    text: str

    def render(self) -> LLMTextMessagePart:
        return {"type": "text", "text": self.text}


class MediaMessagePart(BaseModel):
    content_type: UserMediaContentType
    content: bytes

    def render(self) -> LLMMediaMessagePart:
        return {
            "type": "image_url",
            "image_url": f"data:{self.content_type};base64,{base64.b64encode(self.content).decode()}",
        }


class UserMessage(BaseModel):
    parts: list[TextMessagePart | MediaMessagePart]

    def render(self) -> LLMMessage:
        content: LLMMessage = {
            "role": "user",
            "content": [part.render() for part in self.parts],
        }
        if any(isinstance(part, MediaMessagePart) for part in self.parts):
            content["cache_control"] = {"type": "ephemeral"}
        return content


class AssistantMessage(BaseModel):
    text: str

    def render(self) -> LLMMessage:
        return {"role": "assistant", "content": [{"type": "text", "text": self.text}]}


class SystemMessage(BaseModel):
    text: str

    def render(self) -> LLMMessage:
        return {"role": "system", "content": [{"type": "text", "text": self.text}]}


class AgentResponse[R: BaseModel](BaseModel):
    INPUT_CENTS_PER_MILLION_TOKENS: ClassVar[dict[GeminiModel, float]] = {
        GeminiModel.FLASH_8B: 30,
        GeminiModel.FLASH: 15,
        GeminiModel.PRO: 500,
        GeminiModel.EXP: 0,
    }
    OUTPUT_CENTS_PER_MILLION_TOKENS: ClassVar[dict[GeminiModel, float]] = {
        GeminiModel.FLASH_8B: 30,
        GeminiModel.FLASH: 15,
        GeminiModel.PRO: 500,
        GeminiModel.EXP: 0,
    }

    response: R
    id: str
    flow_name: str
    task_name: str
    model: GeminiModel
    system: SystemMessage | None = None
    input_messages: list[UserMessage | AssistantMessage]
    input_tokens: int
    output_tokens: int
    start_time: datetime
    end_time: datetime

    @computed_field
    @property
    def duration_ms(self) -> int:
        return int((self.end_time - self.start_time).total_seconds() * 1000)

    @computed_field
    @property
    def total_cost(self) -> float:
        input_cost = self.INPUT_CENTS_PER_MILLION_TOKENS[self.model] * self.input_tokens
        output_cost = (
            self.OUTPUT_CENTS_PER_MILLION_TOKENS[self.model] * self.output_tokens
        )
        return input_cost + output_cost
