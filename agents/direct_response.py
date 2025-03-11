from typing import List, Dict
from agents.base import BaseAgent
from langgraph.prebuilt import create_react_agent

class DirectResponseAgent(BaseAgent):
    """Agent for handling general knowledge questions."""
    
    DIRECT_PROMPT = "You are a helpful assistant. Provide a clear, direct answer to the user's question."
    
    def __init__(self, llm):
        """Initialize the direct response agent."""
        super().__init__(llm)
        self.agent = create_react_agent(llm, prompt=self.DIRECT_PROMPT, tools=[])
    
    def process(self, messages: List[Dict[str, str]]) -> str:
        """Process the message using the react agent."""
        result = self.agent.invoke({"messages": messages})
        return result["messages"][-1].content
