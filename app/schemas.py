"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import List, Optional
from app.models import GameStatus, TeamSide


class SportBase(BaseModel):
    """Base sport schema."""
    name: str = Field(..., min_length=1, description="Sport name")
    slug: str = Field(..., min_length=1, description="Sport slug")


class SportCreate(SportBase):
    """Schema for creating a sport."""
    pass


class SportResponse(SportBase):
    """Schema for sport response."""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class GameBase(BaseModel):
    """Base game schema."""
    sport_id: int = Field(..., description="Sport ID")
    team_a_name: str = Field(..., min_length=1, description="Team A name")
    team_b_name: str = Field(..., min_length=1, description="Team B name")
    status: Optional[GameStatus] = GameStatus.SCHEDULED


class GameCreate(GameBase):
    """Schema for creating a game."""
    pass


class GameResponse(GameBase):
    """Schema for game response."""
    id: int
    start_time: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class EventBase(BaseModel):
    """Base event schema."""
    team: TeamSide = Field(..., description="Team side (A or B)")
    minute: int = Field(..., ge=0, description="Minute of the event")
    description: str = Field(..., min_length=1, description="Event description")

    @validator('team', pre=True)
    def validate_team(cls, v):
        """Validate team is A or B."""
        if isinstance(v, str):
            v = v.upper()
            if v not in ['A', 'B']:
                raise ValueError('Team must be A or B')
            return TeamSide[v]
        return v


class EventCreate(EventBase):
    """Schema for creating an event."""
    pass


class EventResponse(EventBase):
    """Schema for event response."""
    id: int
    game_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class GameStateResponse(GameResponse):
    """Schema for game state with events."""
    events: List[EventResponse] = []

    class Config:
        from_attributes = True


class WebSocketEventPayload(BaseModel):
    """Schema for WebSocket event payload."""
    event_id: int
    game_id: int
    team: str
    minute: int
    description: str
    timestamp: datetime

    class Config:
        from_attributes = True

