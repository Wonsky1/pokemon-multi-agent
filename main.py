from contextlib import asynccontextmanager
from http.client import HTTPException
from fastapi import FastAPI, Depends
import uvicorn
from langchain_core.messages import HumanMessage

from agents.factory import AgentFactory
from api.models import ChatRequest
from core.agent_graph import AgentGraph
from core.exceptions import PokemonNotFoundError
from tools.pokeapi import PokeAPIService, get_pokemon_service

agent_graph: AgentGraph | None = None

battle_expert_prompt = """
You are a Pokémon expert analyzing battle scenarios.

Proceed with the analysis and return the winner and reasoning in this format:
{
    "winner": "[Winning Pokémon Name]",
    "reasoning": "[Detailed reasoning explaining why this Pokémon wins, mentioning both competitors]"
}

In the reasoning section, you MUST include:
- Comparison of base stats (HP, Attack, Defense, Special Attack, Special Defense, Speed)
- Type advantages and disadvantages between the two Pokémon
- Effectiveness of moves based on type matchups (e.g., super effective, not very effective)
- Any notable strengths or weaknesses that impact the battle outcome
- A clear explanation of why the winning Pokémon has the advantage

Base stats are more valuable in determining the winner, but type matchups and move effectiveness are also crucial.

Make sure to follow these instructions precisely.
"""

@asynccontextmanager
async def lifespan(app: FastAPI):
    global agent_graph
    agent_graph = AgentGraph()
    
    AgentFactory.register_agent_class(
        "battle_expert", 
        agent_class=AgentFactory._agent_classes["pokemon_expert"],
        default_config={
            "response_format": "simplified",
            "prompt": battle_expert_prompt,
            "tools": []
        }
    )
    
    yield

app = FastAPI(
    lifespan=lifespan,
    title="Pokémon Multi-Agent System",
    description="A multi-agent system for answering Pokémon-related queries",
    version="1.0.0"
)

@app.post("/chat")
async def chat(request: ChatRequest):
    """Chat endpoint."""
    try:
        result = agent_graph.invoke(request.question)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/battle")
async def battle(
    pokemon1: str, 
    pokemon2: str,
    pokemon_service: PokeAPIService = Depends(get_pokemon_service)
):
    """Battle endpoint."""
    try:
        battle_expert = AgentFactory.create_battle_expert(
            response_format="simplified", 
            custom_prompt=battle_expert_prompt
        )
        
        pokemon1_data = pokemon_service.get_pokemon_data(pokemon1)
        pokemon2_data = pokemon_service.get_pokemon_data(pokemon2)

        query = f"Who would win in a battle, {pokemon1}: {pokemon1_data}\nor {pokemon2}: {pokemon2_data}?"
        messages = [{"role": "human", "content": query}]
        result = battle_expert.process(messages)
        return result
        
    except PokemonNotFoundError as e:
        return {
            "winner": "BATTLE_IMPOSSIBLE",
            "reasoning": "Could not analyze the battle due to invalid Pokémon. Please check the spelling of Pokémon names."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to the Pokémon Multi-Agent System API"}
