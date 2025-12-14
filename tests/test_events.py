"""
Phase 3: Play-By-Play Event API Tests

Validate event creation and ordering.
"""
import pytest
from fastapi.testclient import TestClient
import time

# These imports will be available once the app is created
# from app.main import app


class TestEventAPI:
    """Test /games/{game_id}/events endpoints."""
    
    def test_api_post_event_valid(self, client):
        """
        Test: api_post_event_valid
        Intent: POST /games/{game_id}/events adds new event
        Expected: 201 Created, event persisted
        """
        # Create sport and game first
        sport_response = client.post("/sports", json={"name": "Soccer", "slug": "soccer"})
        sport_id = sport_response.json()["id"]
        game_response = client.post("/games", json={
            "sport_id": sport_id,
            "team_a_name": "A",
            "team_b_name": "B"
        })
        game_id = game_response.json()["id"]
        
        # inputs: {team: "A", minute: 10, description: "Goal"}
        response = client.post(f"/games/{game_id}/events", json={
            "team": "A",
            "minute": 10,
            "description": "Goal"
        })
        assert response.status_code == 201
        
        # Verify event is persisted
        get_response = client.get(f"/games/{game_id}")
        assert get_response.status_code == 200
        game_data = get_response.json()
        assert len(game_data["events"]) == 1
        assert game_data["events"][0]["team"] == "A"
        assert game_data["events"][0]["minute"] == 10
        assert game_data["events"][0]["description"] == "Goal"
    
    def test_api_post_event_invalid_team(self, client):
        """
        Test: api_post_event_invalid_team
        Intent: Reject event with invalid team side
        Expected: 400 Validation error
        """
        # Create sport and game first
        sport_response = client.post("/sports", json={"name": "Soccer", "slug": "soccer"})
        sport_id = sport_response.json()["id"]
        game_response = client.post("/games", json={
            "sport_id": sport_id,
            "team_a_name": "A",
            "team_b_name": "B"
        })
        game_id = game_response.json()["id"]
        
        # inputs: {team: "C", minute: 5, description: "Error"}
        response = client.post(f"/games/{game_id}/events", json={
            "team": "C",
            "minute": 5,
            "description": "Error"
        })
        assert response.status_code == 422  # Pydantic validation error
    
    def test_api_event_ordering(self, client):
        """
        Test: api_event_ordering
        Intent: Events returned in chronological order
        Expected: Events sorted by creation time
        """
        # Create sport and game first
        sport_response = client.post("/sports", json={"name": "Soccer", "slug": "soccer"})
        sport_id = sport_response.json()["id"]
        game_response = client.post("/games", json={
            "sport_id": sport_id,
            "team_a_name": "A",
            "team_b_name": "B"
        })
        game_id = game_response.json()["id"]
        
        # Create multiple events with delays
        client.post(f"/games/{game_id}/events", json={"team": "A", "minute": 5, "description": "First"})
        time.sleep(0.01)  # Small delay to ensure different timestamps
        client.post(f"/games/{game_id}/events", json={"team": "B", "minute": 10, "description": "Second"})
        time.sleep(0.01)
        client.post(f"/games/{game_id}/events", json={"team": "A", "minute": 15, "description": "Third"})
        
        # Get game state
        response = client.get(f"/games/{game_id}")
        assert response.status_code == 200
        events = response.json()["events"]
        
        # Verify chronological order
        assert len(events) == 3
        assert events[0]["description"] == "First"
        assert events[1]["description"] == "Second"
        assert events[2]["description"] == "Third"
        
        # Verify timestamps are in order
        for i in range(len(events) - 1):
            from datetime import datetime
            time1 = datetime.fromisoformat(events[i]["created_at"].replace("Z", "+00:00"))
            time2 = datetime.fromisoformat(events[i + 1]["created_at"].replace("Z", "+00:00"))
            assert time1 <= time2

