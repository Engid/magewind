"""Thin wrapper around the model API. Keep vendor-specific code here."""

from dataclasses import dataclass


@dataclass
class Message:
    role: str  # e.g. "user", "assistant", "system"
    content: str


class ModelClient:
    def complete(self, messages: list[Message]) -> Message:
        # TODO: call the model API here and return its reply as a Message.
        raise NotImplementedError


class EchoClient(ModelClient):
    def complete(self, messages: list[Message]) -> Message: 
        return Message(role="assistant", content=f"(echo) {messages[-1].content}")