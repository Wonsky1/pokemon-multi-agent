from typing import List, Dict
from tools.langchain_tools import pokeapi_tool
from agents.base import BaseAgent
from langgraph.prebuilt import create_react_agent

class ResearcherAgent(BaseAgent):
    """Agent responsible for fetching and providing data from external sources."""
    
    def __init__(self, llm):
        """Initialize the researcher agent."""
        super().__init__(llm)
        
        prompt = """You are a researcher. When asked about Pokémon, use the provided tool to fetch data from the PokéAPI. Provide a clear, comprehensive answer that directly addresses the user's question."""
        
        self.agent = create_react_agent(llm, tools=[pokeapi_tool], prompt=prompt)
    
    def process(self, messages: List[Dict[str, str]]) -> str:
        """Process the message using the react agent."""
        result = self.agent.invoke({"messages": messages})
        return result["messages"][-1].content
