import unittest
from unittest.mock import AsyncMock, Mock, patch
import httpx
from tools import pokeapi
from tools.pokeapi import PokeAPIService
from core.exceptions import PokemonNotFoundError
from tools.langchain_tools import AsyncPokeapiTool, AsyncPokeapiToolWithTypes
from tools.langchain_tools import PokemonInput



# ------------------------------------
# pokeapi.py tests
# ------------------------------------


class TestPokeAPIService(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.service = PokeAPIService(cache_size=2)

    async def asyncTearDown(self):
        await self.service.close()

    @patch("tools.pokeapi.httpx.AsyncClient.get")
    async def test_pokemon_exists_true(self, mock_get):
        mock_response = AsyncMock()
        mock_response.json = Mock(return_value={"name": "pikachu"})
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        exists = await self.service.pokemon_exists("pikachu")

        self.assertTrue(exists)
        mock_get.assert_awaited_once_with(f"{self.service.BASE_URL}/pokemon/pikachu")

    @patch("tools.pokeapi.httpx.AsyncClient.get")
    async def test_pokemon_exists_false(self, mock_get):
        mock_get.side_effect = PokemonNotFoundError("Pokémon not found")

        exists = await self.service.pokemon_exists("unknownpokemon")

        self.assertFalse(exists)
        mock_get.assert_awaited_once()

    @patch("tools.pokeapi.httpx.AsyncClient.get")
    async def test_get_pokemon_data_with_cache(self, mock_get):
        mock_response = AsyncMock()
        mock_response.json = Mock(return_value={
            "id": 25,
            "name": "pikachu",
            "base_experience": 112,
            "height": 4,
            "weight": 60,
            "abilities": [{"ability": {"name": "static"}}],
            "stats": [{"stat": {"name": "speed"}, "base_stat": 90}],
            "types": [{"type": {"name": "electric"}}],
        })
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        data = await self.service.get_pokemon_data("pikachu")

        expected_data = {
            "id": 25,
            "name": "pikachu",
            "base_experience": 112,
            "height": 4,
            "weight": 60,
            "abilities": ["static"],
            "stats": {"speed": 90},
            "types": ["electric"],
        }

        self.assertEqual(data, expected_data)
        self.assertIn("pikachu_False", self.service.pokemon_cache)
        mock_get.assert_awaited_once()

        mock_get.reset_mock()

        cached_data = await self.service.get_pokemon_data("pikachu")
        self.assertEqual(cached_data, expected_data)
        mock_get.assert_not_called()

    @patch("tools.pokeapi.httpx.AsyncClient.get")
    async def test_get_pokemon_data_not_found(self, mock_get):
        mock_get.side_effect = PokemonNotFoundError("Pokémon not found")

        with self.assertRaises(PokemonNotFoundError):
            await self.service.get_pokemon_data("unknownpokemon")

        mock_get.assert_awaited_once()

    @patch("tools.pokeapi.httpx.AsyncClient.get")
    async def test_get_type_data_with_cache(self, mock_get):
        mock_response = AsyncMock()
        mock_response.json = Mock(return_value={
            "id": 13,
            "name": "electric",
            "damage_relations": {
                "double_damage_to": [{"name": "water"}],
                "half_damage_from": [{"name": "electric"}],
            },
        })
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        type_data = await self.service.get_type_data("electric")

        expected_data = {
            "id": 13,
            "name": "electric",
            "damage_relations": {
                "double_damage_to": [{"name": "water"}],
                "half_damage_from": [{"name": "electric"}],
            },
        }

        self.assertEqual(type_data, expected_data)
        self.assertIn("electric", self.service.type_cache)
        mock_get.assert_awaited_once()

        mock_get.reset_mock()

        cached_data = await self.service.get_type_data("electric")
        self.assertEqual(cached_data, expected_data)
        mock_get.assert_not_called()

    @patch("tools.pokeapi.PokeAPIService._fetch_type_data")
    @patch("tools.pokeapi.httpx.AsyncClient.get")
    async def test_get_pokemon_data_with_type_details(self, mock_get, mock_fetch_type_data):
        mock_response = AsyncMock()
        mock_response.json = Mock(return_value={
            "id": 25,
            "name": "pikachu",
            "base_experience": 112,
            "height": 4,
            "weight": 60,
            "abilities": [{"ability": {"name": "static"}}],
            "stats": [{"stat": {"name": "speed"}, "base_stat": 90}],
            "types": [{"type": {"name": "electric"}}],
        })
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        mock_fetch_type_data.return_value = {
            "damage_relations": {
                "double_damage_to": [{"name": "water"}],
            },
        }

        data = await self.service.get_pokemon_data("pikachu", get_type_data=True)

        expected_data = {
            "id": 25,
            "name": "pikachu",
            "base_experience": 112,
            "height": 4,
            "weight": 60,
            "abilities": ["static"],
            "stats": {"speed": 90},
            "types": ["electric"],
            "type_details": {
                "electric": {
                    "double_damage_to": [{"name": "water"}],
                }
            },
        }

        self.assertEqual(data, expected_data)
        mock_get.assert_awaited_once()
        mock_fetch_type_data.assert_awaited_once_with("electric")

    async def test_cache_eviction_policy(self):
        self.service.pokemon_cache = {
            "bulbasaur_False": {},
            "charmander_False": {},
        }

        with patch.object(self.service, '_fetch_pokemon_data', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = {"id": 7, "name": "squirtle"}

            await self.service.get_pokemon_data("squirtle")

            self.assertEqual(len(self.service.pokemon_cache), 2)
            self.assertIn("squirtle_False", self.service.pokemon_cache)
            self.assertNotIn("bulbasaur_False", self.service.pokemon_cache)

    @patch("tools.pokeapi.httpx.AsyncClient.get")
    async def test_fetch_type_data_error(self, mock_get):
        mock_get.side_effect = httpx.HTTPError("HTTP error")

        with self.assertRaises(ValueError):
            await self.service._fetch_type_data("unknown")

        mock_get.assert_awaited_once()

    async def test_service_close(self):
        with patch.object(self.service.client, 'aclose', new_callable=AsyncMock) as mock_aclose:
            await self.service.close()
            mock_aclose.assert_awaited_once()


class TestGlobalPokemonServiceLifecycle(unittest.IsolatedAsyncioTestCase):
    async def asyncTearDown(self):
        if pokeapi.pokemon_service:
            await pokeapi.pokemon_service.close()
            pokeapi.pokemon_service = None

    def test_initialize_pokemon_service_sets_global_instance(self):
        pokeapi.pokemon_service = None
        pokeapi.initialize_pokemon_service()
        self.assertIsInstance(pokeapi.pokemon_service, pokeapi.PokeAPIService)

    async def test_shutdown_pokemon_service_closes_instance(self):
        pokeapi.initialize_pokemon_service()
        with patch.object(pokeapi.pokemon_service, 'close', new_callable=AsyncMock) as mock_close:
            await pokeapi.shutdown_pokemon_service()
            mock_close.assert_awaited_once()

    def test_get_pokemon_service_returns_instance(self):
        pokeapi.pokemon_service = None
        service = pokeapi.get_pokemon_service()
        self.assertIsInstance(service, pokeapi.PokeAPIService)
        self.assertIs(service, pokeapi.pokemon_service)

    def test_get_pokemon_service_reuses_existing_instance(self):
        """Test that get_pokemon_service returns existing instance if already initialized."""
        service1 = pokeapi.PokeAPIService()
        pokeapi.pokemon_service = service1
        service2 = pokeapi.get_pokemon_service()
        self.assertIs(service1, service2)


# ------------------------------------
# pokeapi.py tests
# ------------------------------------


class TestAsyncPokeapiTool(unittest.IsolatedAsyncioTestCase):
    """Test suite for AsyncPokeapiTool."""

    async def asyncSetUp(self):
        """Set up the AsyncPokeapiTool instance before each test."""
        self.tool = AsyncPokeapiTool()

    @patch("tools.langchain_tools.get_pokemon_service")
    async def test_arun_returns_pokemon_data(self, mock_get_service):
        """Test that _arun returns Pokémon data from the service."""
        mock_service = AsyncMock()
        mock_service.get_pokemon_data.return_value = {"name": "pikachu"}
        mock_get_service.return_value = mock_service

        result = await self.tool._arun(pokemon_name="pikachu")

        self.assertEqual(result, {"name": "pikachu"})
        mock_service.get_pokemon_data.assert_awaited_once_with("pikachu")

    def test_run_raises_not_implemented_error(self):
        """Test that _run raises NotImplementedError as it should not be used."""
        with self.assertRaises(NotImplementedError):
            self.tool._run(pokemon_name="pikachu")


class TestAsyncPokeapiToolWithTypes(unittest.IsolatedAsyncioTestCase):
    """Test suite for AsyncPokeapiToolWithTypes."""

    async def asyncSetUp(self):
        """Set up the AsyncPokeapiToolWithTypes instance before each test."""
        self.tool = AsyncPokeapiToolWithTypes()

    @patch("tools.langchain_tools.get_pokemon_service")
    async def test_arun_returns_pokemon_data_with_types(self, mock_get_service):
        """Test that _arun returns Pokémon data including type damage relations."""
        mock_service = AsyncMock()
        mock_service.get_pokemon_data.return_value = {
            "name": "pikachu",
            "type_details": {"electric": {"double_damage_to": [{"name": "water"}]}}
        }
        mock_get_service.return_value = mock_service

        result = await self.tool._arun(pokemon_name="pikachu")

        self.assertEqual(result, {
            "name": "pikachu",
            "type_details": {"electric": {"double_damage_to": [{"name": "water"}]}}
        })
        mock_service.get_pokemon_data.assert_awaited_once_with("pikachu", get_type_data=True)

    def test_run_raises_not_implemented_error(self):
        """Test that _run raises NotImplementedError as it should not be used."""
        with self.assertRaises(NotImplementedError):
            self.tool._run(pokemon_name="pikachu")


def test_pokemon_input_schema():
    data = PokemonInput(pokemon_name="pikachu")
    assert data.pokemon_name == "pikachu"
