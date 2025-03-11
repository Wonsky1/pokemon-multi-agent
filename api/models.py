from pydantic import BaseModel, Field
from typing import Optional

class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    question: str = Field(..., description="The user's question")

class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    answer: str = Field(..., description="The answer to the user's question")
    reasoning: Optional[str] = Field(None, description="Reasoning behind the answer")

class BattleResponse(BaseModel):
    """Response model for battle endpoint."""
    winner: str = Field(..., description="The likely winner of the battle")
    reasoning: str = Field(..., description="Reasoning behind the prediction")
