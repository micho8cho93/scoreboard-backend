"""
Phase 1: Domain Model Tests

Validate models before any API implementation.
"""
import pytest
from pydantic import ValidationError
from app.models import Sport, Game, PlayByPlayEvent, GameStatus, TeamSide
from app.schemas import SportCreate, GameCreate, EventCreate


class TestSportModel:
    """Test Sport model validation."""
    
    def test_sport_model_valid(self):
        """
        Test: sport_model_valid
        Intent: Ensure sport creation with valid data succeeds
        Expected: Sport instance created successfully
        """
        # inputs: {name: "Soccer", slug: "soccer"}
        sport_data = SportCreate(name="Soccer", slug="soccer")
        assert sport_data.name == "Soccer"
        assert sport_data.slug == "soccer"
    
    def test_sport_model_invalid_name(self):
        """
        Test: sport_model_invalid_name
        Intent: Reject sport creation with empty name
        Expected: Validation error
        """
        # inputs: {name: "", slug: "empty"}
        with pytest.raises(ValidationError):
            SportCreate(name="", slug="empty")


class TestGameModel:
    """Test Game model validation."""
    
    def test_game_model_valid(self):
        """
        Test: game_model_valid
        Intent: Game requires sport association and two teams
        Expected: Game instance created successfully
        """
        # inputs: {sport_id: 1, team_a: "A", team_b: "B"}
        game_data = GameCreate(sport_id=1, team_a_name="A", team_b_name="B")
        assert game_data.sport_id == 1
        assert game_data.team_a_name == "A"
        assert game_data.team_b_name == "B"
    
    def test_game_model_invalid_status(self):
        """
        Test: game_model_invalid_status
        Intent: Reject invalid game status
        Expected: Validation error
        """
        # inputs: {status: "unknown"}
        # Note: Pydantic will accept the string but it won't match the enum
        # We test that invalid enum values are rejected
        with pytest.raises(ValidationError):
            GameCreate(sport_id=1, team_a_name="A", team_b_name="B", status="unknown")


class TestEventModel:
    """Test Event model validation."""
    
    def test_event_model_valid(self):
        """
        Test: event_model_valid
        Intent: Event must belong to a game and have team/minute
        Expected: Event created successfully
        """
        # inputs: {game_id: 1, team: "A", minute: 5, description: "Goal"}
        event_data = EventCreate(team="A", minute=5, description="Goal")
        assert event_data.team == TeamSide.A
        assert event_data.minute == 5
        assert event_data.description == "Goal"

