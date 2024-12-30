from typing import Annotated, Literal, Sequence, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph import MessagesState, add_messages
from pydantic import BaseModel, Field


class OregonTrailResponse(BaseModel):
    free_form: str = Field(
        description="Free form response to the question for non multiple choice responses or for additional clarity"
    )
    multiple_choice_response: Literal["A", "B", "C", "D"] = Field(
        description="Single character response to the question for multiple choice questions. Must be either A, B, C, or D."
    )


class AgentState(MessagesState):
    pass
    # final_response: OregonTrailResponse
