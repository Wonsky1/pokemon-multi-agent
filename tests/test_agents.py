import unittest
from unittest.mock import AsyncMock, patch, MagicMock
from langchain_core.messages import HumanMessage

from agents.supervisor import SupervisorAgent

# ------------------------------------
# supervisor.py tests
# ------------------------------------


class TestSupervisorAgent(unittest.IsolatedAsyncioTestCase):
    """
    Test suite for SupervisorAgent in agents.supervisor.
    Covers raw and structured routing, direct responses, and error handling.
    """

    async def asyncSetUp(self):
        """
        Set up a SupervisorAgent instance with a mocked LLM.
        """
        self.agent = SupervisorAgent(AsyncMock())
        self.agent.llm = AsyncMock()

    async def test_raw_routing_to_researcher(self):
        """
        Test raw routing where the LLM responds with 'researcher'.
        """
        self.agent.llm.ainvoke.return_value.content = "researcher"
        messages = [HumanMessage(content="Find some facts about Pikachu")]
        result = await self.agent.process(messages)
        self.assertEqual(result, "researcher")

    async def test_raw_routing_to_pokemon_expert(self):
        """
        Test raw routing where the LLM responds with 'pokemon_expert'.
        """
        self.agent.llm.ainvoke.return_value.content = "pokemon_expert"
        messages = [HumanMessage(content="Tell me about Pikachu's type")]
        result = await self.agent.process(messages)
        self.assertEqual(result, "pokemon_expert")

    async def test_raw_routing_to_direct_response(self):
        """
        Test raw routing where LLM responds with 'direct_response' and triggers direct generation.
        """
        self.agent.llm.ainvoke.side_effect = [
            MagicMock(content="direct_response"),
            MagicMock(content="Pikachu is a yellow electric Pokémon."),
        ]
        messages = [HumanMessage(content="What is Pikachu?")]
        result = await self.agent.process(messages)
        self.assertEqual(result, {"answer": "Pikachu is a yellow electric Pokémon."})

    @patch("agents.supervisor.Router")
    async def test_structured_routing_to_researcher(self, mock_router):
        """
        Test structured routing where the LLM responds with a Router object for 'researcher'.
        """
        self.agent.llm.ainvoke.return_value.content = "invalid"

        structured_llm_mock = MagicMock()
        structured_llm_mock.ainvoke = AsyncMock()

        mock_response = MagicMock()
        mock_response.next = "researcher"
        structured_llm_mock.ainvoke.return_value = mock_response

        self.agent.llm.with_structured_output = MagicMock(return_value=structured_llm_mock)

        messages = [HumanMessage(content="Tell me some Pokémon facts")]
        result = await self.agent.process(messages)
        self.assertEqual(result, "researcher")

    @patch("agents.supervisor.Router")
    async def test_structured_routing_to_direct_response(self, mock_router):
        """
        Test structured routing with 'direct_response' triggering direct response generation.
        """
        self.agent.llm.ainvoke.return_value.content = "invalid"
    
        structured_llm_mock = MagicMock()
        structured_llm_mock.ainvoke = AsyncMock()

        mock_response = MagicMock()
        mock_response.next = "direct_response"
        structured_llm_mock.ainvoke.return_value = mock_response

        self.agent.llm.with_structured_output = MagicMock(return_value=structured_llm_mock)

        self.agent.llm.ainvoke = AsyncMock()
        self.agent.llm.ainvoke.return_value.content = "Pikachu is an electric mouse Pokémon."

        messages = [HumanMessage(content="Who is Pikachu?")]
        result = await self.agent.process(messages)
        self.assertEqual(result, {"answer": "Pikachu is an electric mouse Pokémon."})


    async def test_invalid_raw_then_invalid_structured_returns_none(self):
        """
        Test behavior when both raw and structured routing fail or return invalid data.
        """
        self.agent.llm.ainvoke.side_effect = Exception("Raw failure")
        self.agent.llm.with_structured_output.return_value.ainvoke.side_effect = Exception("Structured failure")

        messages = [HumanMessage(content="Unusual query")]
        result = await self.agent.process(messages)
        self.assertIsNone(result)
