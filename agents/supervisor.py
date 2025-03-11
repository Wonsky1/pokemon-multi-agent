from typing import Dict, List, Union
from agents.base import BaseAgent
from agents.models import Router
from langchain_core.messages.base import BaseMessage


class SupervisorAgent(BaseAgent):
    """Supervisor agent for routing requests to appropriate specialized agents."""
    VALID_OPTIONS = ["researcher", "pokemon_expert", "direct_response"]
    
    SYSTEM_PROMPT = """
    You are a supervisor tasked with classifying user questions.
    
    Given the user's message, classify it into ONE of these categories:
    
    1. researcher: For questions about Pokémon facts or data
       Example: "What are the base stats of Charizard?"
       
    2. pokemon_expert: For questions about Pokémon analysis or battle scenarios
       Example: "Who would win in a battle, Pikachu or Bulbasaur?"
       
    3. direct_response: For ANY basic questions not specifically about Pokémon
       Example: "What's your name?", "Hello", "My name is Vlad", etc.
    """

    RAW_CALL_SUFFIX: str = """    
    IMPORTANT: Respond with ONLY ONE WORD - either "researcher", "pokemon_expert", or "direct_response".
    Do not include any other text, explanations, or formatting.
    """

    STRUCTURED_CALL_SUFFIX: str = """
    You must respond with a valid JSON object containing the key "next" with one of these three values.
    
    For example:
    {"next": "direct_response"}
    
    Always use this exact JSON format - nothing else. No explanations, no additional text.
    """
    
    async def process(self, messages: List[BaseMessage]) -> Union[str, Dict[str, str]]:
        """Determine which agent should handle the request or respond directly."""
        for approach in ("structured", "raw"):
            try:
                if approach == "raw":
                    llm_messages = [{"role": "system", "content": self.SYSTEM_PROMPT + self.RAW_CALL_SUFFIX}] + messages
                    raw_response = (await self.llm.ainvoke(llm_messages)).content.strip().lower()
                    if raw_response == "direct_response":
                        direct_message = messages[-1].content
                        return await self._generate_direct_response(direct_message)
                    elif raw_response in self.VALID_OPTIONS:
                        return raw_response
                else:
                    llm_messages = [{"role": "system", "content": self.SYSTEM_PROMPT + self.STRUCTURED_CALL_SUFFIX}] + messages
                    structured_response = await self.llm.with_structured_output(Router).ainvoke(llm_messages)
                    if structured_response.next == "direct_response":
                        direct_message = messages[-1].content
                        return await self._generate_direct_response(direct_message)
                    elif structured_response.next in self.VALID_OPTIONS:
                        return structured_response.next
            except Exception as e:
                print(f"Error in {approach} approach: {str(e)}")
                
    async def _generate_direct_response(self, message: str) -> Dict[str, str]:
        """Generate a direct response to basic questions."""
        direct_prompt = """You are a helpful assistant. Provide a clear, concise response to the user's question or message.
        Keep your response friendly but brief."""
        llm_messages = [
            {"role": "system", "content": direct_prompt},
            {"role": "user", "content": message}
        ]
        response = (await self.llm.ainvoke(llm_messages)).content
        return {"answer": response}
