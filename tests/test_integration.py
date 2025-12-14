"""
Phase 5: Integration Tests

Ensure REST and WebSocket layers work together.
"""
import pytest
import asyncio
from fastapi.testclient import TestClient
import time

# These imports will be available once the app is created
# from app.main import app


class TestFullGameFlow:
    """Test complete game flow with REST and WebSocket."""
    
    def test_full_game_flow(self, client):
        """
        Test: full_game_flow
        Intent: Simulate creating sport, game, event and receiving via WebSocket
        Expected: Event appears in REST and real-time updates
        """
        # 1. Create a sport
        sport_response = client.post("/sports", json={"name": "Soccer", "slug": "soccer"})
        assert sport_response.status_code == 201
        sport_id = sport_response.json()["id"]
        
        # 2. Create a game
        game_response = client.post("/games", json={
            "sport_id": sport_id,
            "team_a_name": "Team A",
            "team_b_name": "Team B"
        })
        assert game_response.status_code == 201
        game_id = game_response.json()["id"]
        
        # 3. Connect WebSocket client
        with client.websocket_connect(f"/ws/games/{game_id}") as websocket:
            # 4. Create an event via REST
            event_response = client.post(f"/games/{game_id}/events", json={
                "team": "A",
                "minute": 15,
                "description": "Goal scored!"
            })
            assert event_response.status_code == 201
            
            # 5. Verify event appears in REST API
            game_state = client.get(f"/games/{game_id}").json()
            assert len(game_state["events"]) == 1
            assert game_state["events"][0]["description"] == "Goal scored!"
            
            # 6. Verify event received via WebSocket
            ws_data = websocket.receive_json()
            assert ws_data["description"] == "Goal scored!"
            assert ws_data["team"] == "A"
            assert ws_data["minute"] == 15
    
    def test_concurrent_events(self, client):
        """
        Test: concurrent_events
        Intent: Multiple events posted rapidly
        Expected: All events broadcasted in order, no duplicates
        """
        # Create a sport and game
        sport_response = client.post("/sports", json={"name": "Soccer", "slug": "soccer"})
        sport_id = sport_response.json()["id"]
        game_response = client.post("/games", json={
            "sport_id": sport_id,
            "team_a_name": "A",
            "team_b_name": "B"
        })
        game_id = game_response.json()["id"]
        
        # Connect WebSocket client
        with client.websocket_connect(f"/ws/games/{game_id}") as websocket:
            # Post multiple events rapidly
            events = [
                {"team": "A", "minute": 5, "description": "Event 1"},
                {"team": "B", "minute": 10, "description": "Event 2"},
                {"team": "A", "minute": 15, "description": "Event 3"},
            ]
            
            for event in events:
                client.post(f"/games/{game_id}/events", json=event)
            
            # Receive all events via WebSocket
            received_events = []
            for _ in range(3):
                received_events.append(websocket.receive_json())
            
            # Verify all events received
            assert len(received_events) == 3
            
            # Verify order (should match creation order)
            assert received_events[0]["description"] == "Event 1"
            assert received_events[1]["description"] == "Event 2"
            assert received_events[2]["description"] == "Event 3"
            
            # Verify no duplicates
            descriptions = [e["description"] for e in received_events]
            assert len(descriptions) == len(set(descriptions))

