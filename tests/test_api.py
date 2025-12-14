"""
Phase 2: REST API Contract Tests

Ensure backend API endpoints adhere to contract.
"""
import pytest
from fastapi.testclient import TestClient


class TestSportsAPI:
    """Test /sports endpoint."""
    
    def test_api_get_sports_empty(self, client):
        """
        Test: api_get_sports_empty
        Intent: GET /sports returns empty list initially
        Expected: []
        """
        response = client.get("/sports")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_api_post_sport(self, client):
        """
        Test: api_post_sport
        Intent: POST /sports creates sport
        Expected: 201 Created, sport appears in GET
        """
        # inputs: {name: "Basketball", slug: "basketball"}
        response = client.post("/sports", json={"name": "Basketball", "slug": "basketball"})
        assert response.status_code == 201
        
        # Verify it appears in GET
        get_response = client.get("/sports")
        assert get_response.status_code == 200
        sports = get_response.json()
        assert len(sports) == 1
        assert sports[0]["name"] == "Basketball"
        assert sports[0]["slug"] == "basketball"


class TestGamesAPI:
    """Test /games endpoints."""
    
    def test_api_get_games_empty(self, client):
        """
        Test: api_get_games_empty
        Intent: GET /sports/{sport_id}/games returns empty initially
        Expected: []
        """
        # First create a sport
        sport_response = client.post("/sports", json={"name": "Soccer", "slug": "soccer"})
        sport_id = sport_response.json()["id"]
        
        response = client.get(f"/sports/{sport_id}/games")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_api_post_game(self, client):
        """
        Test: api_post_game
        Intent: POST /games creates a game for a sport
        Expected: 201 Created, associated with sport
        """
        # First create a sport
        sport_response = client.post("/sports", json={"name": "Soccer", "slug": "soccer"})
        sport_id = sport_response.json()["id"]
        
        # inputs: {sport_id: 1, team_a: "A", team_b: "B"}
        response = client.post("/games", json={
            "sport_id": sport_id,
            "team_a_name": "A",
            "team_b_name": "B"
        })
        assert response.status_code == 201
        
        # Verify it's associated with sport
        get_response = client.get(f"/sports/{sport_id}/games")
        assert get_response.status_code == 200
        games = get_response.json()
        assert len(games) == 1
        assert games[0]["team_a_name"] == "A"
        assert games[0]["team_b_name"] == "B"
    
    def test_api_get_game_state(self, client):
        """
        Test: api_get_game_state
        Intent: GET /games/{game_id} returns metadata and play-by-play
        Expected: Game metadata + empty play-by-play list
        """
        # Create sport and game
        sport_response = client.post("/sports", json={"name": "Soccer", "slug": "soccer"})
        sport_id = sport_response.json()["id"]
        game_response = client.post("/games", json={
            "sport_id": sport_id,
            "team_a_name": "A",
            "team_b_name": "B"
        })
        game_id = game_response.json()["id"]
        
        response = client.get(f"/games/{game_id}")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "sport_id" in data
        assert "team_a_name" in data
        assert "team_b_name" in data
        assert "events" in data
        assert data["events"] == []

