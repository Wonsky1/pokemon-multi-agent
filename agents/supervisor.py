from typing import Literal, TypedDict, Dict, List
from agents.base import BaseAgent

class Router(TypedDict):
    """Worker to route to next."""
    next: Literal["researcher", "pokemon_expert", "direct_response"]

class SupervisorAgent(BaseAgent):
    """Supervisor agent for routing requests to appropriate specialized agents."""
    
    SYSTEM_PROMPT = """
        You are a supervisor tasked with classifying user questions. Given the following user request, determine the appropriate category:
        If the question is basic and not about Pokémon, respond with:
        direct_response
        If the question is about Pokémon facts or data (e.g., "What are the base stats of Charizard?"), respond with:
        researcher
        If the question is about Pokémon analysis or battle scenarios (e.g., "Who would win in a battle, Pikachu or Bulbasaur?"), respond with:
        pokemon_expert
        Output only one of these responses: researcher, pokemon_expert, or direct_response.
    """
    
    def process(self, messages: List[Dict[str, str]]) -> str:
        """Determine which agent should handle the request."""
        llm_messages = [{"role": "system", "content": self.SYSTEM_PROMPT}] + messages
        response = self.llm.with_structured_output(Router).invoke(llm_messages)
        return response["next"]
