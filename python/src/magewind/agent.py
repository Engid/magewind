"""The agent loop."""

from magewind.model import Message, ModelClient


class Agent:
    def __init__(self, client: ModelClient) -> None:
        self.client = client
        self.history: list[Message] = []

    def step(self, user_input: str) -> Message:
        self.history.append(Message(role="user", content=user_input))
        reply = self.client.complete(self.history)
        self.history.append(reply)
        # TODO: inspect reply for tool calls, run them, loop until done.
        return reply

