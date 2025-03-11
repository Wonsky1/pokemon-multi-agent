from abc import ABC, abstractmethod
from typing import Dict, List

class BaseAgent(ABC):
    """Base class for all agents."""
    
    def __init__(self, llm):
        """Initialize the agent with an LLM."""
        self.llm = llm
    
    @abstractmethod
    def process(self, messages: List[Dict[str, str]]) -> str:
        """Process messages and return a response."""
        pass
