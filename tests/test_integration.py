from main import app
from typing import Any

from fastapi.testclient import TestClient

import pytest
from fastapi.testclient import TestClient
from typing import Any

from core.config import settings

def verify_result_with_llm(expected_result: Any, actual_result: Any) -> bool:
    """Invoke the generative model to verify if the actual result matches the expected result."""
    prompt = f"""
        Compare the following Pokémon battle result:
        Expected winner: {expected_result}
        Actual winner: {actual_result}
        
        Do these match exactly? Answer with only a single word: 'true' or 'false'.
    """

    response = settings.GENERATIVE_MODEL.invoke(prompt)
    answer = response.content.strip().lower()
    
    return answer == "true"




@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


@pytest.mark.integration
@pytest.mark.parametrize("question, expected_answer", [
    ("What is the capital of France?", "paris"),
    ("What is the largest planet in our solar system?", "jupiter"),
    ("What is the fastest land animal?", "cheetah"),
])
def test_chat_direct_question(client, question, expected_answer):
    """Test successful response from /chat endpoint with various direct questions."""
    payload = {"question": question}
    response = client.post("/chat", json=payload)
    assert response.status_code == 200
    json_response = response.json()
    answer = json_response["answer"]
    assert expected_answer in answer.lower()

@pytest.mark.integration
@pytest.mark.parametrize("pokemon_name, expected_stats", [
    ("pikachu", {"hp": 35, "attack": 55, "defense": 40, "special_attack": 50, "special_defense": 50, "speed": 90}),
    ("bulbasaur", {"hp": 45, "attack": 49, "defense": 49, "special_attack": 65, "special_defense": 65, "speed": 45}),
    ("charmander", {"hp": 39, "attack": 52, "defense": 43, "special_attack": 60, "special_defense": 50, "speed": 65}),
])
def test_chat_researcher_correct_pokemon(client, pokemon_name, expected_stats):
    """Test successful response from /chat endpoint for base stats of various Pokémon."""
    payload = {"question": f"What are the base stats for {pokemon_name}?"}
    response = client.post("/chat", json=payload)
    assert response.status_code == 200
    json_response = response.json()
    stats = json_response["base_stats"]
    assert stats == expected_stats


@pytest.mark.integration
@pytest.mark.parametrize("pokemon1, pokemon2, expected_winner", [
    ("pikachu", "squirtle", "pikachu"),
    ("charmander", "blastoise", "blastoise"),
])
def test_chat_battle_winner(client, pokemon1, pokemon2, expected_winner):
    """Test successful response from /chat endpoint for battle outcomes between Pokémon."""
    payload = {"question": f"Who wins: {pokemon1} or {pokemon2}?"}
    response = client.post("/chat", json=payload)
    assert response.status_code == 200
    json_response = response.json()
    answer = json_response["answer"]
    assert verify_result_with_llm(f"expected to win: {expected_winner}", f"actual winner - {answer}")

@pytest.mark.integration
@pytest.mark.parametrize("pokemon1, pokemon2, expected_winner", [
    ("pikachu", "squirtle", "pikachu"),  
    ("charmander", "bulbasaur", "charmander"),  
])
def test_battle_existent_pokemons(client, pokemon1, pokemon2, expected_winner):
    """Test successful response from /battle endpoint for normal Pokémon."""
    response = client.get(f"/battle?pokemon1={pokemon1}&pokemon2={pokemon2}")
    assert response.status_code == 200
    json_response = response.json()
    winner = json_response["winner"]
    
    assert verify_result_with_llm(expected_winner, winner)

@pytest.mark.integration
@pytest.mark.parametrize("pokemon1, pokemon2", [
    ("nonexistentpokemon1", "nonexistentpokemon2"),  
    ("pikachu", "nonexistentpokemon"),  
])
def test_battle_with_nonexistent_pokemons(client, pokemon1, pokemon2):
    """Test response from /battle endpoint when one or both Pokémon do not exist."""
    response = client.get(f"/battle?pokemon1={pokemon1}&pokemon2={pokemon2}")
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["winner"] == "BATTLE_IMPOSSIBLE"
    assert json_response["reasoning"] == "Could not analyze the battle due to invalid Pokémon. Please check the spelling of Pokémon names."

