from functools import cached_property
from typing import TYPE_CHECKING, Iterator, Type, TypeVar

import instructor
from pydantic import BaseModel

from ..logging import logger
from ..settings import settings
from ._base import BaseProvider

if TYPE_CHECKING:
    from ..models import Conversation, Message

T = TypeVar("T", bound=BaseModel)


class Groq(BaseProvider):
    NAME = "groq"
    DEFAULT_MODEL = "llama3-8b-8192"
    DEFAULT_MAX_TOKENS = 1_000
    DEFAULT_KWARGS = {"max_tokens": DEFAULT_MAX_TOKENS}
    supports_streaming = True

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.get_api_key(self.NAME)

    @cached_property
    def client(self):
        """The raw Groq client."""
        if not self.api_key:
            raise ValueError("Groq API key is required")
        try:
            import groq
        except ImportError as exc:
            raise ImportError(
                "Please install the `groq` package: `pip install groq`"
            ) from exc
        return groq.Groq(api_key=self.api_key)

    @cached_property
    def structured_client(self):
        """A client patched with Instructor."""
        return instructor.from_groq(self.client)

    @logger
    def send_conversation(
        self,
        conversation: "Conversation",
        **kwargs,
    ) -> "Message":
        """Send a conversation to the Groq API."""
        from ..models import Message

        messages = [
            {"role": msg.role, "content": msg.text} for msg in conversation.messages
        ]

        response = self.client.chat.completions.create(
            model=conversation.llm_model or self.DEFAULT_MODEL,
            messages=messages,
            **{**self.DEFAULT_KWARGS, **kwargs},
        )

        # Get the response content from the Groq response
        assistant_message = response.choices[0].message

        # Create and return a properly formatted Message instance
        return Message(
            role="assistant",
            text=assistant_message.content or "",
            raw=response,
            llm_model=conversation.llm_model or self.DEFAULT_MODEL,
            llm_provider=self.NAME,
        )

    @logger
    def structured_response(self, prompt: str, response_model: Type[T], **kwargs) -> T:
        # Ensure messages are provided in kwargs
        messages = [
            {"role": "user", "content": prompt},
        ]

        response = self.structured_client.chat.completions.create(
            messages=messages,
            response_model=response_model,
            model=kwargs.pop("llm_model", self.DEFAULT_MODEL),
            **{**self.DEFAULT_KWARGS, **kwargs},
        )
        return response_model.model_validate(response)

    @logger
    def generate_text(
        self,
        prompt: str,
        *,
        llm_model: str,
        **kwargs,
    ) -> str:
        messages = [
            {"role": "user", "content": prompt},
        ]

        response = self.client.chat.completions.create(
            messages=messages,
            model=llm_model or self.DEFAULT_MODEL,
            **{**self.DEFAULT_KWARGS, **kwargs},
        )

        return str(response.choices[0].message.content)

    @logger
    def generate_stream_text(
        self,
        prompt: str,
        *,
        llm_model: str | None = None,
        **kwargs,
    ) -> Iterator[str]:
        """Generate streaming text using the Groq API."""
        messages = [
            {"role": "user", "content": prompt},
        ]

        response = self.client.chat.completions.create(
            messages=messages,
            model=llm_model or self.DEFAULT_MODEL,
            stream=True,
            **{**self.DEFAULT_KWARGS, **kwargs},
        )

        try:
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            raise RuntimeError(
                f"Failed to generate streaming text with Groq API: {e}"
            ) from e
