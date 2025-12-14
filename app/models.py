"""
Database models for Sport, Game, and PlayByPlayEvent.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class GameStatus(enum.Enum):
    """Game status enumeration."""
    SCHEDULED = "Scheduled"
    LIVE = "Live"
    FINISHED = "Finished"


class TeamSide(enum.Enum):
    """Team side enumeration."""
    A = "A"
    B = "B"


class Sport(Base):
    """Sport model."""
    __tablename__ = "sports"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    slug = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    games = relationship("Game", back_populates="sport")


class Game(Base):
    """Game model."""
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    sport_id = Column(Integer, ForeignKey("sports.id"), nullable=False)
    team_a_name = Column(String, nullable=False)
    team_b_name = Column(String, nullable=False)
    status = Column(Enum(GameStatus), default=GameStatus.SCHEDULED, nullable=False)
    start_time = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    sport = relationship("Sport", back_populates="games")
    events = relationship("PlayByPlayEvent", back_populates="game", order_by="PlayByPlayEvent.created_at")


class PlayByPlayEvent(Base):
    """Play-by-play event model."""
    __tablename__ = "play_by_play_events"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    team = Column(Enum(TeamSide), nullable=False)
    minute = Column(Integer, nullable=False)
    description = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    game = relationship("Game", back_populates="events")

