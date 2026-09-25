from magewind.agent import Agent
from magewind.model import Message, ModelClient


class EchoClient(ModelClient):
    """Fake client so tests don't need the real API."""

    def complete(self, messages: list[Message]) -> Message:
        return Message(role="assistant", content=messages[-1].content)


def test_step_records_history():
    agent = Agent(EchoClient())
    reply = agent.step("hi")
    assert reply.content == "hi"
    assert len(agent.history) == 2
