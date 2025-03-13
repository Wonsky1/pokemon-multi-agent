import unittest
from unittest.mock import AsyncMock, patch, MagicMock
from langchain_core.messages import HumanMessage

from agents.base import BaseAgent
from agents.supervisor import SupervisorAgent
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from agents.pokemon_expert import PokemonExpertAgent
from agents.models import DetailedPokemonBattle
from agents.researcher import ResearcherAgent
from core.config import ResponseFormat, settings, AgentType, PokemonNotFoundStatus

from agents.factory import (
    AgentFactory,
    get_agent_factory,
    get_supervisor_agent,
    get_researcher_agent,
    get_pokemon_expert_agent,
    get_battle_expert_agent,
)


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
        self.assertEqual(result, AgentType.RESEARCHER.value)

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

        self.agent.llm.with_structured_output = MagicMock(
            return_value=structured_llm_mock
        )

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

        self.agent.llm.with_structured_output = MagicMock(
            return_value=structured_llm_mock
        )

        self.agent.llm.ainvoke = AsyncMock()
        self.agent.llm.ainvoke.return_value.content = (
            "Pikachu is an electric mouse Pokémon."
        )

        messages = [HumanMessage(content="Who is Pikachu?")]
        result = await self.agent.process(messages)
        self.assertEqual(result, {"answer": "Pikachu is an electric mouse Pokémon."})

    async def test_invalid_raw_then_invalid_structured_returns_none(self):
        """
        Test behavior when both raw and structured routing fail or return invalid data.
        """
        self.agent.llm.ainvoke.side_effect = Exception("Raw failure")
        structured_llm_mock = MagicMock()
        structured_llm_mock.ainvoke = AsyncMock(
            side_effect=Exception("Structured failure")
        )

        self.agent.llm.with_structured_output = MagicMock(
            return_value=structured_llm_mock
        )

        messages = [HumanMessage(content="Unusual query")]
        result = await self.agent.process(messages)
        self.assertIsNone(result)


# ------------------------------------
# factory.py tests
# ------------------------------------


class TestAgentFactory(unittest.TestCase):
    """
    Test suite for the AgentFactory and dependency providers.
    """

    def setUp(self):
        AgentFactory._instances = {}
        AgentFactory._agent_classes = {}
        AgentFactory._default_configs = {}
        AgentFactory.initialize()

    def test_initialize_sets_agent_classes_and_configs(self):
        """
        Test AgentFactory.initialize sets expected agent classes and configs.
        """
        self.assertIn("supervisor", AgentFactory._agent_classes)
        self.assertIn("researcher", AgentFactory._agent_classes)
        self.assertIn("pokemon_expert", AgentFactory._agent_classes)

        self.assertIn("supervisor", AgentFactory._default_configs)
        self.assertIsInstance(AgentFactory._default_configs["supervisor"], dict)

    def test_get_agent_returns_singleton_instance(self):
        """
        Test get_agent returns cached instance if already created.
        """
        agent1 = AgentFactory.get_agent("supervisor")
        agent2 = AgentFactory.get_agent("supervisor")
        self.assertIs(agent1, agent2)

    def test_get_agent_with_custom_config_returns_new_instance(self):
        """
        Test get_agent with kwargs bypasses cache and creates new agent.
        """
        default_agent = AgentFactory.get_agent("pokemon_expert")
        custom_agent = AgentFactory.get_agent(
            "pokemon_expert", response_format=ResponseFormat.SIMPLIFIED
        )
        self.assertIsNot(default_agent, custom_agent)

    def test_get_agent_invalid_type_raises(self):
        """
        Test get_agent raises ValueError for unknown agent type.
        """
        with self.assertRaises(ValueError):
            AgentFactory.get_agent("invalid_type")

    def test_register_agent_class_registers_new_agent(self):
        """
        Test register_agent_class correctly registers a new agent type.
        """

        class MockAgent(BaseAgent):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)

            async def process(self, messages):
                return "mock_result"

        AgentFactory.register_agent_class("mock_agent", MockAgent)

        self.assertIn("mock_agent", AgentFactory._agent_classes)
        self.assertEqual(AgentFactory._default_configs["mock_agent"], {})

        instance = AgentFactory.get_agent("mock_agent")
        self.assertIsInstance(instance, MockAgent)

    def test_create_battle_expert_with_tool_and_prompt(self):
        """
        Test create_battle_expert creates a configured agent with tool and prompt.
        """
        mock_agent_cls = MagicMock()
        mock_instance = MagicMock()
        mock_agent_cls.return_value = mock_instance

        AgentFactory._agent_classes["pokemon_expert"] = mock_agent_cls

        agent = AgentFactory.create_battle_expert(
            response_format=ResponseFormat.DETAILED,
            custom_prompt="Analyze battle strategy",
        )

        mock_agent_cls.assert_called_once()
        call_args = mock_agent_cls.call_args[1]

        self.assertEqual(call_args["response_format"], ResponseFormat.DETAILED)
        self.assertEqual(call_args["prompt"], "Analyze battle strategy")
        self.assertIn("tools", call_args)
        self.assertIs(agent, mock_instance)

    def test_create_battle_expert_without_tool(self):
        """
        Test create_battle_expert with use_tool=False skips tool injection.
        """
        mock_agent_cls = MagicMock()
        mock_instance = MagicMock()
        mock_agent_cls.return_value = mock_instance

        AgentFactory._agent_classes["pokemon_expert"] = mock_agent_cls

        agent = AgentFactory.create_battle_expert(use_tool=False)

        mock_agent_cls.assert_called_once()
        call_args = mock_agent_cls.call_args[1]

        self.assertEqual(call_args["response_format"], ResponseFormat.SIMPLIFIED)
        self.assertNotIn("prompt", call_args)
        self.assertEqual(call_args["tools"], [])
        self.assertIs(agent, mock_instance)

    def test_get_agent_factory_returns_singleton(self):
        """
        Test get_agent_factory returns same instance across calls.
        """
        factory1 = get_agent_factory()
        factory2 = get_agent_factory()
        self.assertIs(factory1, factory2)

    def test_get_supervisor_agent_returns_instance(self):
        """
        Test get_supervisor_agent returns a valid SupervisorAgent.
        """
        agent = get_supervisor_agent()
        self.assertEqual(agent.__class__.__name__, "SupervisorAgent")

    def test_get_researcher_agent_returns_instance(self):
        """
        Test get_researcher_agent returns a valid ResearcherAgent.
        """
        agent = get_researcher_agent()
        self.assertEqual(agent.__class__.__name__, "ResearcherAgent")

    def test_get_pokemon_expert_agent_returns_instance(self):
        """
        Test get_pokemon_expert_agent returns a valid PokemonExpertAgent.
        """
        agent = get_pokemon_expert_agent()
        self.assertEqual(agent.__class__.__name__, "PokemonExpertAgent")

    def test_get_battle_expert_agent_returns_custom_battle_expert(self):
        """
        Test get_battle_expert_agent returns a valid specialized PokemonExpertAgent.
        """
        mock_agent_cls = MagicMock()
        mock_instance = MagicMock()
        mock_agent_cls.return_value = mock_instance

        AgentFactory._agent_classes["pokemon_expert"] = mock_agent_cls

        agent = get_battle_expert_agent(
            response_format=ResponseFormat.DETAILED,
            custom_prompt="Focus on battle analysis",
        )

        mock_agent_cls.assert_called_once()
        call_args = mock_agent_cls.call_args[1]

        self.assertEqual(call_args["response_format"], ResponseFormat.DETAILED)
        self.assertEqual(call_args["prompt"], "Focus on battle analysis")
        self.assertIs(agent, mock_instance)


# ------------------------------------
# pokemon_expert.py tests
# ------------------------------------


class TestPokemonExpertAgent(unittest.IsolatedAsyncioTestCase):
    """
    Test suite for PokemonExpertAgent in agents.pokemon_expert.
    """

    @patch("agents.pokemon_expert.create_react_agent")
    async def test_process_returns_detailed_battle_result(
        self, mock_create_react_agent
    ):
        """
        Test process() returns a DetailedPokemonBattle result.
        """
        mock_agent = AsyncMock()
        mock_create_react_agent.return_value = mock_agent

        expected_result = DetailedPokemonBattle(
            winner="Pikachu",
            reasoning="Pikachu is faster.",
            answer="Pikachu wins the battle due to its speed and effectiveness.",
        )
        mock_agent.ainvoke.return_value = {"structured_response": expected_result}

        agent = PokemonExpertAgent(llm=MagicMock())
        result = await agent.process([{"content": "Pikachu vs Squirtle"}])

        self.assertEqual(result, expected_result)
        mock_agent.ainvoke.assert_awaited_once()

    @patch("agents.pokemon_expert.create_react_agent")
    async def test_process_fallback_on_exception(self, mock_create_react_agent):
        """
        Test fallback returns a SimplifiedPokemonBattle on failure.
        """
        mock_agent = AsyncMock()
        mock_agent.ainvoke.side_effect = Exception("LLM error")
        mock_create_react_agent.return_value = mock_agent

        agent = PokemonExpertAgent(llm=MagicMock())
        result = await agent.process([{"content": "Invalid input"}])

        self.assertIsInstance(result, DetailedPokemonBattle)
        self.assertEqual(result.answer, PokemonNotFoundStatus.ANSWER_IMPOSSIBLE)


# ------------------------------------
# researcher.py tests
# ------------------------------------


class TestResearcherAgent(unittest.IsolatedAsyncioTestCase):
    """
    Test suite for ResearcherAgent in agents.researcher.
    Covers successful data retrieval and fallback behavior.
    """

    @patch("agents.researcher.create_react_agent")
    async def test_process_returns_pokemon_data(self, mock_create_react_agent):
        """
        Test process() returns structured Pokémon data.
        """
        mock_agent = AsyncMock()
        mock_create_react_agent.return_value = mock_agent

        expected_data = {
            "name": "pikachu",
            "base_stats": {
                "hp": 35,
                "attack": 55,
                "defense": 40,
                "special_attack": 50,
                "special_defense": 50,
                "speed": 90,
            },
        }

        mock_agent.ainvoke.return_value = {"structured_response": expected_data}

        agent = ResearcherAgent(llm=MagicMock())
        result = await agent.process([{"content": "Tell me about Pikachu"}])

        self.assertEqual(result, expected_data)
        mock_agent.ainvoke.assert_awaited_once()

    @patch("agents.researcher.create_react_agent")
    async def test_process_returns_default_on_failure(self, mock_create_react_agent):
        """
        Test fallback returns default stats on agent failure.
        """
        mock_agent = AsyncMock()
        mock_agent.ainvoke.side_effect = Exception("Tool error")
        mock_create_react_agent.return_value = mock_agent

        agent = ResearcherAgent(llm=MagicMock())
        result = await agent.process([{"content": "Unknown Pokémon"}])

        self.assertEqual(result["name"], "NOT_FOUND")
        self.assertEqual(result["base_stats"]["hp"], 0)
        self.assertEqual(result["base_stats"]["speed"], 0)
