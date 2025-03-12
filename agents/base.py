from abc import ABC, abstractmethod
from typing import Dict, List, Any


class BaseAgent(ABC):
    """Base class for all agents with async support."""

    def __init__(self, llm):
        """Initialize the agent with an LLM."""
        self.llm = llm

    @abstractmethod
    async def process(self, messages: List[Dict[str, str]]) -> Any:
        """Process messages and return a response asynchronously."""
        pass
