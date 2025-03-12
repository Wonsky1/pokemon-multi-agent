import unittest
from unittest.mock import AsyncMock, patch, Mock
from fastapi.testclient import TestClient
from core.exceptions import PokemonNotFoundError
from main import app, lifespan
from pytest import MonkeyPatch


class TestRootEndpoint(unittest.TestCase):
    """Test suite for the root endpoint."""

    def setUp(self):
        self.client = TestClient(app)

    def test_root_endpoint(self):
        """Test that the root endpoint returns a welcome message."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"message": "Welcome to the Pokémon Multi-Agent System API"},
        )


class TestChatEndpoint(unittest.IsolatedAsyncioTestCase):
    """Test suite for the chat endpoint."""

    def setUp(self):
        self.client = TestClient(app)

    @patch("main.agent_graph")
    async def test_chat_success(self, mock_agent_graph):
        """Test successful response from /chat endpoint."""
        mock_agent_graph.invoke = AsyncMock(
            return_value={"response": "Hello from agent"}
        )
        payload = {"question": "What is Pikachu?"}
        response = self.client.post("/chat", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"response": "Hello from agent"})
        mock_agent_graph.invoke.assert_awaited_once_with("What is Pikachu?")

    @patch("main.agent_graph")
    @patch("main.logger")
    async def test_chat_internal_server_error(self, mock_logger, mock_agent_graph):
        """Test that /chat returns 500 if an exception occurs."""
        mock_agent_graph.invoke = AsyncMock(
            side_effect=Exception("Mocked internal error")
        )
        payload = {"question": "Test error"}
        response = self.client.post("/chat", json=payload)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()["detail"], "Mocked internal error")
        mock_logger.error.assert_called()


class TestBattleEndpoint(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

        patcher = patch("tools.pokeapi.PokeAPIService", autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_pokeapi_service_class = patcher.start()
        self.mock_service = AsyncMock()
        self.mock_pokeapi_service_class.return_value = self.mock_service

    def tearDown(self):
        app.dependency_overrides = {}

    def test_battle_success(self):
        self.mock_service.get_pokemon_data.side_effect = [
            {"name": "pikachu", "type_details": {}},
            {"name": "bulbasaur", "type_details": {}},
        ]

        with patch("main.battle_expert") as mock_battle_expert:
            mock_battle_expert.process = AsyncMock(
                return_value={"winner": "pikachu", "reasoning": "Speed advantage"}
            )

            response = self.client.get("/battle?pokemon1=pikachu&pokemon2=bulbasaur")

            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.json(), {"winner": "pikachu", "reasoning": "Speed advantage"}
            )

    def test_battle_pokemon_not_found(self):
        with patch("main.battle_expert") as mock_battle_expert:
            mock_battle_expert.process.side_effect = PokemonNotFoundError(
                "Pokemon not found"
            )

            response = self.client.get("/battle?pokemon1=invilad&pokemon2=invalid")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["winner"], "BATTLE_IMPOSSIBLE")
        self.mock_service.get_pokemon_data.side_effect = None
        self.mock_service.get_pokemon_data.reset_mock()

    def test_battle_internal_error(self):
        self.mock_service.get_pokemon_data.side_effect = Exception("Unexpected error")

        response = self.client.get("/battle?pokemon1=a&pokemon2=b")

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()["detail"], "Unexpected error")
        self.mock_service.get_pokemon_data.side_effect = None
        self.mock_service.get_pokemon_data.reset_mock()


class TestLifespan(unittest.IsolatedAsyncioTestCase):
    """Test suite for lifespan startup/shutdown logic."""

    @patch("main.get_agent_factory")
    @patch("main.get_agent_graph")
    @patch("main.initialize_pokemon_service")
    @patch("main.shutdown_pokemon_service")
    @patch("main.logger")
    async def test_lifespan_starts_and_stops(
        self,
        mock_logger,
        mock_shutdown,
        mock_initialize,
        mock_get_graph,
        mock_get_factory,
    ):
        """Test that lifespan starts and stops system services correctly."""
        mock_get_graph.return_value = Mock()
        mock_get_factory.return_value.create_battle_expert.return_value = Mock()

        async with lifespan(app):
            mock_initialize.assert_called_once()
            mock_get_graph.assert_called_once()
            mock_get_factory.return_value.create_battle_expert.assert_called_once()

        mock_shutdown.assert_called_once()
        mock_logger.info.assert_any_call("Initializing the Pokémon Multi-Agent System")
        mock_logger.info.assert_any_call("System initialization complete")
        mock_logger.info.assert_any_call("Shutting down the Pokémon Multi-Agent System")
        mock_logger.info.assert_any_call("System shutdown complete")
