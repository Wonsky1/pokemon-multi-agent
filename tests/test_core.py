import unittest
from unittest.mock import AsyncMock, patch, MagicMock
from langchain_core.messages import HumanMessage, AIMessage

from core.agent_graph import AgentGraph, get_agent_graph

# ------------------------------------
# agent_graph.py tests
# ------------------------------------


class TestAgentGraph(unittest.IsolatedAsyncioTestCase):
    """
    Test suite for the AgentGraph class in core.agent_graph.
    Validates agent orchestration, node behavior, and message handling.
    """

    async def asyncSetUp(self):
        """
        Set up the test by patching the agent factory and mocking agents.
        """
        patcher_factory = patch("core.agent_graph.get_agent_factory")
        self.mock_factory = patcher_factory.start()
        self.addCleanup(patcher_factory.stop)

        self.mock_supervisor = AsyncMock()
        self.mock_researcher = AsyncMock()
        self.mock_pokemon_expert = AsyncMock()

        self.mock_factory_instance = MagicMock()
        self.mock_factory_instance.get_agent.side_effect = lambda role: {
            "supervisor": self.mock_supervisor,
            "researcher": self.mock_researcher,
            "pokemon_expert": self.mock_pokemon_expert,
        }[role]

        self.mock_factory.return_value = self.mock_factory_instance

        self.agent_graph = AgentGraph()

    async def test_supervisor_returns_direct_answer(self):
        """
        Test when supervisor responds directly with an answer and ends the flow.
        """
        self.mock_supervisor.process.return_value = {"answer": "Final response."}
        result = await self.agent_graph.invoke("What is Pikachu?")
        self.assertEqual(result, {"answer": "Final response."})
        self.mock_supervisor.process.assert_awaited_once()

    async def test_supervisor_delegates_to_researcher(self):
        """
        Test when supervisor delegates the task to the researcher agent.
        """
        self.mock_supervisor.process.return_value = "researcher"
        self.mock_researcher.process.return_value = {
            "facts": ["Pikachu is an electric type."]
        }

        result = await self.agent_graph.invoke("Tell me about Pikachu.")
        self.assertEqual(result, {"facts": ["Pikachu is an electric type."]})

        self.mock_supervisor.process.assert_awaited_once()
        self.mock_researcher.process.assert_awaited_once()

    async def test_supervisor_delegates_to_pokemon_expert(self):
        """
        Test when supervisor delegates the task to the Pokémon expert agent.
        """
        self.mock_supervisor.process.return_value = "pokemon_expert"
        self.mock_pokemon_expert.process.return_value = {
            "data": "Pikachu is an Electric-type Pokémon."
        }

        result = await self.agent_graph.invoke("Tell me about Pikachu's abilities.")
        self.assertEqual(result, {"data": "Pikachu is an Electric-type Pokémon."})

        self.mock_supervisor.process.assert_awaited_once()
        self.mock_pokemon_expert.process.assert_awaited_once()

    def test_get_agent_graph_reuses_instance(self):
        """
        Test that get_agent_graph returns a singleton instance.
        """
        graph1 = get_agent_graph()
        graph2 = get_agent_graph()
        self.assertIs(graph1, graph2)
