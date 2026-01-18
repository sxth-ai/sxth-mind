"""Tests for the HTTP API."""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Check if fastapi is available
pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient

from examples.sales import SalesAdapter
from sxth_mind.api import create_app
from sxth_mind.providers.base import BaseLLMProvider, LLMResponse
from sxth_mind.storage import MemoryStorage


class MockProvider(BaseLLMProvider):
    """Mock LLM provider for testing."""

    @property
    def default_model(self) -> str:
        return "mock-model"

    async def chat(self, messages, model=None, tools=None, temperature=0.7, max_tokens=None):
        return LLMResponse(content="Mock API response", model="mock-model")

    async def chat_stream(self, messages, model=None, tools=None, temperature=0.7, max_tokens=None):
        for word in ["Mock", "streaming", "response"]:
            yield word + " "


class TestAPIHealth:
    """Test health endpoint."""

    @pytest.fixture
    def client(self):
        app = create_app(
            adapter=SalesAdapter(),
            storage=MemoryStorage(),
            provider=MockProvider(),
        )
        return TestClient(app)

    def test_health_check(self, client):
        """Health endpoint should return status."""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert data["adapter"] == "sales"
        assert "Storage" in data["storage"]


class TestAPIChat:
    """Test chat endpoints."""

    @pytest.fixture
    def client(self):
        app = create_app(
            adapter=SalesAdapter(),
            storage=MemoryStorage(),
            provider=MockProvider(),
        )
        return TestClient(app)

    def test_chat_basic(self, client):
        """POST /chat should return a response."""
        response = client.post(
            "/chat",
            json={"user_id": "user_1", "message": "Hello!"},
        )
        assert response.status_code == 200

        data = response.json()
        assert data["response"] == "Mock API response"
        assert data["user_id"] == "user_1"
        assert data["project_id"] == "default"

    def test_chat_with_project_id(self, client):
        """POST /chat should support custom project_id."""
        response = client.post(
            "/chat",
            json={
                "user_id": "user_1",
                "message": "Working on Acme deal",
                "project_id": "deal_acme",
            },
        )
        assert response.status_code == 200

        data = response.json()
        assert data["project_id"] == "deal_acme"

    def test_chat_missing_user_id(self, client):
        """POST /chat should require user_id."""
        response = client.post(
            "/chat",
            json={"message": "Hello!"},
        )
        assert response.status_code == 422  # Validation error

    def test_chat_missing_message(self, client):
        """POST /chat should require message."""
        response = client.post(
            "/chat",
            json={"user_id": "user_1"},
        )
        assert response.status_code == 422


class TestAPIState:
    """Test state endpoints."""

    @pytest.fixture
    def client(self):
        app = create_app(
            adapter=SalesAdapter(),
            storage=MemoryStorage(),
            provider=MockProvider(),
        )
        return TestClient(app)

    def test_get_state_new_user(self, client):
        """GET /state/{user_id} should return null for new users."""
        response = client.get("/state/unknown_user")
        assert response.status_code == 200

        data = response.json()
        assert data["user_mind"] is None

    def test_get_state_after_chat(self, client):
        """GET /state/{user_id} should return state after chat."""
        # First, have a conversation
        client.post("/chat", json={"user_id": "user_1", "message": "Hello!"})

        # Then get state
        response = client.get("/state/user_1")
        assert response.status_code == 200

        data = response.json()
        assert data["user_mind"] is not None
        assert data["user_mind"]["user_id"] == "user_1"

    def test_get_state_with_project_id(self, client):
        """GET /state/{user_id}?project_id=X should include project."""
        # First, have a conversation
        client.post(
            "/chat",
            json={
                "user_id": "user_1",
                "message": "Hello!",
                "project_id": "proj_1",
            },
        )

        # Then get state
        response = client.get("/state/user_1?project_id=proj_1")
        assert response.status_code == 200

        data = response.json()
        assert data["project_mind"] is not None
        assert data["project_mind"]["project_id"] == "proj_1"


class TestAPIExplain:
    """Test explain endpoint."""

    @pytest.fixture
    def client(self):
        app = create_app(
            adapter=SalesAdapter(),
            storage=MemoryStorage(),
            provider=MockProvider(),
        )
        return TestClient(app)

    def test_explain_new_user(self, client):
        """GET /explain/{user_id} should handle new users."""
        response = client.get("/explain/unknown_user")
        assert response.status_code == 200

        data = response.json()
        assert "No state found" in data["explanation"]

    def test_explain_after_chat(self, client):
        """GET /explain/{user_id} should return explanation after chat."""
        client.post("/chat", json={"user_id": "user_1", "message": "Hello!"})

        response = client.get("/explain/user_1")
        assert response.status_code == 200

        data = response.json()
        assert "user_1" in data["explanation"]
        assert data["user_id"] == "user_1"


class TestAPINudges:
    """Test nudge endpoints."""

    @pytest.fixture
    def client(self):
        app = create_app(
            adapter=SalesAdapter(),
            storage=MemoryStorage(),
            provider=MockProvider(),
        )
        return TestClient(app)

    def test_get_nudges_new_user(self, client):
        """GET /nudges/{user_id} should return empty list for new users."""
        response = client.get("/nudges/user_1")
        assert response.status_code == 200

        data = response.json()
        assert data == []

    def test_dismiss_nudge(self, client):
        """POST /nudges/{nudge_id}/dismiss should work."""
        response = client.post("/nudges/nudge_123/dismiss")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "dismissed"
        assert data["nudge_id"] == "nudge_123"

    def test_act_on_nudge(self, client):
        """POST /nudges/{nudge_id}/act should work."""
        response = client.post("/nudges/nudge_123/act")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "acted"
        assert data["nudge_id"] == "nudge_123"


class TestAPICreateApp:
    """Test create_app() factory."""

    def test_create_app_with_cors(self):
        """create_app() should support CORS configuration."""
        app = create_app(
            adapter=SalesAdapter(),
            cors_origins=["http://localhost:3000"],
        )
        assert app is not None

    def test_create_app_minimal(self):
        """create_app() should work with minimal config."""
        app = create_app(adapter=SalesAdapter())
        assert app is not None
