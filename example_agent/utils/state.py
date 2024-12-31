from typing import Annotated, Literal, Sequence, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph import MessagesState, add_messages
from pydantic import BaseModel, Field


class MultipleChoiceResponse(BaseModel):
    multiple_choice_response: Literal["A", "B", "C", "D"] = Field(
        description="Single character response to the question for multiple choice questions. Must be either A, B, C, or D."
    )


class AgentState(MessagesState):
    multi_choice_response: MultipleChoiceResponse
