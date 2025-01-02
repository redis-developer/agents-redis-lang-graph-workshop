from typing import Literal

from langgraph.graph import MessagesState
from pydantic import BaseModel, Field


class MultipleChoiceResponse(BaseModel):
    multiple_choice_response: Literal["A", "B", "C", "D"] = Field(
        description="Single character response to the question for multiple choice questions. Must be either A, B, C, or D."
    )


class AgentState(MessagesState):
    multi_choice_response: MultipleChoiceResponse
