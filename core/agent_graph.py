from typing import Dict, Any, List, Literal
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import MessagesState, END, StateGraph, START
from langgraph.types import Command
from agents.models import PokemonData
from agents.supervisor import SupervisorAgent
from agents.researcher import ResearcherAgent
from agents.pokemon_expert import PokemonExpertAgent
from agents.direct_response import DirectResponseAgent
from core.config import settings

class State(MessagesState):
    """State for the multi-agent system."""
    next: str

class AgentGraph:
    """Multi-agent orchestration graph."""
    
    def __init__(self):
        """Initialize the agent graph."""
        self.llm = settings.GENERATIVE_MODEL
        self.supervisor = SupervisorAgent(self.llm)
        self.researcher = ResearcherAgent(self.llm)
        self.pokemon_expert = PokemonExpertAgent(self.llm)
        self.direct_response = DirectResponseAgent(self.llm)
        self.graph = self._build_graph()
    
    def _supervisor_node(self, state: Dict[str, Any]) -> Command[Literal["researcher", "pokemon_expert", "direct_response"]]:
        """Supervisor node function."""
        next_agent = self.supervisor.process(state["messages"])
        return Command(goto=next_agent, update={"next": next_agent})
    
    def _researcher_node(self, state: State) -> Command[Literal["__end__"]]:
        """Researcher node function."""
        result = self.researcher.process(state["messages"])
        
        structured_message = AIMessage(
            content="",
            additional_kwargs={"structured_output": result}
        )
        
        return Command(
            update={"messages": state["messages"] + [structured_message]},
            goto=END
        )
    
    def _pokemon_expert_node(self, state: State) -> Command[Literal["__end__"]]:
        """Pokémon expert node function."""
        result = self.pokemon_expert.process(state["messages"])
        structured_message = AIMessage(
            content="",
            additional_kwargs={"structured_output": result}
        )
        
        return Command(
            update={"messages": state["messages"] + [structured_message]},
            goto=END
        )
    
    def _direct_response_node(self, state: State) -> Command[Literal["__end__"]]:
        """Direct response node function."""
        result = self.direct_response.process(state["messages"])
        return Command(
            update={"messages": state["messages"] + [AIMessage(content=result)]},
            goto=END
        )

    def _build_graph(self) -> StateGraph:
        """Build the agent graph."""
        builder = StateGraph(State)
        builder.add_edge(START, "supervisor")
        builder.add_node("supervisor", self._supervisor_node)
        builder.add_node("researcher", self._researcher_node)
        builder.add_node("pokemon_expert", self._pokemon_expert_node)
        builder.add_node("direct_response", self._direct_response_node)
        return builder.compile()
    
    def invoke(self, question: str) -> PokemonData | Dict[str, str]:
        """Invoke the agent graph with a question.
        
        Returns:
            - PokemonData model when the researcher agent is used
            - Dict[str, str] with an "answer" key when other agents are used
        """
        result = self.graph.invoke({
            "messages": [HumanMessage(content=question)]
        })
        
        last_message = result["messages"][-1]
        if hasattr(last_message, "additional_kwargs") and "structured_output" in last_message.additional_kwargs:
            structured_output = last_message.additional_kwargs["structured_output"]
            return structured_output
        else:
            return {
                "answer": last_message.content
            }
