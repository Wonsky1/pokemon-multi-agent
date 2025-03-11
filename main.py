from contextlib import asynccontextmanager
from http.client import HTTPException
from fastapi import FastAPI
import uvicorn

from api.models import ChatRequest
from core.agent_graph import AgentGraph


agent_graph: AgentGraph | None = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global agent_graph
    agent_graph = AgentGraph()
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


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to the Pokémon Multi-Agent System API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
