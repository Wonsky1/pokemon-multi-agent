import unittest
from main import app
from typing import Any

from fastapi.testclient import TestClient

import pytest
from fastapi.testclient import TestClient
from typing import Any

@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client

@pytest.mark.integration
def test_chat_direct_question(client):
    """Test successful response from /chat endpoint."""
    payload = {"question": "What is the capital of France?"}
    response = client.post("/chat", json=payload)
    assert response.status_code == 200
    json_response = response.json()
    answer = json_response["answer"]
    assert "paris" in answer.lower()
