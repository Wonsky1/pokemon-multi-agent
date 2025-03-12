from typing import Dict, Any, Literal
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import MessagesState, END, StateGraph, START
from langgraph.types import Command
from agents.factory import get_agent_factory
from core.config import settings


class State(MessagesState):
    """State for the multi-agent system."""

    next: str


class AgentGraph:
    """Multi-agent orchestration graph with async support."""

    def __init__(self):
        """Initialize the agent graph."""
        self.llm = settings.GENERATIVE_MODEL
        factory = get_agent_factory()
        self.supervisor = factory.get_agent("supervisor")
        self.researcher = factory.get_agent("researcher")
        self.pokemon_expert = factory.get_agent("pokemon_expert")
        self.graph = self._build_graph()

    async def _supervisor_node(
        self, state: Dict[str, Any]
    ) -> Command[Literal["researcher", "pokemon_expert", "__end__"]]:
        """Supervisor node function."""
        result = await self.supervisor.process(state["messages"])

        if isinstance(result, dict) and "answer" in result:
            return Command(
                update={
                    "messages": state["messages"]
                    + [AIMessage(content=result["answer"])]
                },
                goto=END,
            )

        return Command(goto=result, update={"next": result})

    async def _researcher_node(self, state: State) -> Command[Literal["__end__"]]:
        """Researcher node function."""
        result = await self.researcher.process(state["messages"])

        structured_message = AIMessage(
            content="", additional_kwargs={"structured_output": result}
        )

        return Command(
            update={"messages": state["messages"] + [structured_message]}, goto=END
        )

    async def _pokemon_expert_node(self, state: State) -> Command[Literal["__end__"]]:
        """Pokémon expert node function."""
        result = await self.pokemon_expert.process(state["messages"])
        structured_message = AIMessage(
            content="", additional_kwargs={"structured_output": result}
        )

        return Command(
            update={"messages": state["messages"] + [structured_message]}, goto=END
        )

    def _build_graph(self) -> StateGraph:
        """Build the agent graph."""
        builder = StateGraph(State)
        builder.add_edge(START, "supervisor")
        builder.add_node("supervisor", self._supervisor_node)
        builder.add_node("researcher", self._researcher_node)
        builder.add_node("pokemon_expert", self._pokemon_expert_node)

        builder.add_edge("supervisor", END)

        return builder.compile()

    async def invoke(self, question: str) -> Dict[str, Any]:
        """Invoke the agent graph with a question asynchronously."""
        result = await self.graph.ainvoke(
            {"messages": [HumanMessage(content=question)]}
        )

        last_message = result["messages"][-1]
        if (
            hasattr(last_message, "additional_kwargs")
            and "structured_output" in last_message.additional_kwargs
        ):
            structured_output = last_message.additional_kwargs["structured_output"]
            return structured_output
        else:
            return {"answer": last_message.content}


agent_graph = None


def get_agent_graph() -> AgentGraph:
    """Dependency provider for the AgentGraph."""
    global agent_graph
    if agent_graph is None:
        agent_graph = AgentGraph()
    return agent_graph
