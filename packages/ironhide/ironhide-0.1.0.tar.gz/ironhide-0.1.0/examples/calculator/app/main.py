import json

from fastapi import FastAPI
from ironhide import BaseAgent
from pydantic import BaseModel

app = FastAPI()


class Request(BaseModel):
    """User Message to Agent."""

    content: str


class Response(BaseModel):
    """Agent Message to User."""

    result: int


class Calculator(BaseAgent):
    """You are a calculator agent."""

    model = "gpt-4o-mini"
    response_format = Response

    def add(self, a: int, b: int) -> int:
        """Add two integers and returns the result integer."""
        return a + b

    def multiply(self, a: int, b: int) -> int:
        """Multiply two integers and returns the result integer."""
        return a * b


@app.post("/")
async def agent_message(
    message: Request,
) -> Response:
    """Get response from agent."""
    agent = Calculator()
    response = await agent.chat(message.content)
    return Response(**json.loads(response))
