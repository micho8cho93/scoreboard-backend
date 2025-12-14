"""
FastAPI application main file.
"""
from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict
import json
from datetime import datetime

from app.database import get_db, init_db
from app import models, schemas

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title="Real-Time Scoreboard API",
    description="Live play-by-play scoreboard application",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://micho8cho93.github.io",
        "https://micho8cho93.github.io/scoreboard_frontend",
        "https://micho8cho93.github.io/scoreboard_frontend/",
    ],  # In production, restrict to GitHub Pages domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    """Manages WebSocket connections per game."""
    
    def __init__(self):
        # game_id -> List[WebSocket]
        self.active_connections: Dict[int, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, game_id: int):
        """Connect a client to a game's WebSocket."""
        await websocket.accept()
        if game_id not in self.active_connections:
            self.active_connections[game_id] = []
        self.active_connections[game_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, game_id: int):
        """Disconnect a client from a game's WebSocket."""
        if game_id in self.active_connections:
            if websocket in self.active_connections[game_id]:
                self.active_connections[game_id].remove(websocket)
            if not self.active_connections[game_id]:
                del self.active_connections[game_id]
    
    async def broadcast(self, game_id: int, message: dict):
        """Broadcast a message to all connected clients for a game."""
        if game_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[game_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    disconnected.append(connection)
            
            # Remove disconnected clients
            for conn in disconnected:
                self.disconnect(conn, game_id)


manager = ConnectionManager()


# REST API Endpoints

@app.get("/sports", response_model=List[schemas.SportResponse])
def get_sports(db: Session = Depends(get_db)):
    """
    GET /sports
    List all sports.
    """
    sports = db.query(models.Sport).all()
    return sports


@app.post("/sports", response_model=schemas.SportResponse, status_code=201)
def create_sport(sport: schemas.SportCreate, db: Session = Depends(get_db)):
    """
    POST /sports
    Create a new sport.
    """
    # Check if sport with same name or slug exists
    existing = db.query(models.Sport).filter(
        (models.Sport.name == sport.name) | (models.Sport.slug == sport.slug)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Sport with this name or slug already exists")
    
    db_sport = models.Sport(**sport.dict())
    db.add(db_sport)
    db.commit()
    db.refresh(db_sport)
    return db_sport


@app.get("/sports/{sport_id}/games", response_model=List[schemas.GameResponse])
def get_sport_games(sport_id: int, db: Session = Depends(get_db)):
    """
    GET /sports/{sport_id}/games
    List games for a sport.
    """
    # Verify sport exists
    sport = db.query(models.Sport).filter(models.Sport.id == sport_id).first()
    if not sport:
        raise HTTPException(status_code=404, detail="Sport not found")
    
    games = db.query(models.Game).filter(models.Game.sport_id == sport_id).all()
    return games


@app.post("/games", response_model=schemas.GameResponse, status_code=201)
def create_game(game: schemas.GameCreate, db: Session = Depends(get_db)):
    """
    POST /games
    Create a new game.
    """
    # Verify sport exists
    sport = db.query(models.Sport).filter(models.Sport.id == game.sport_id).first()
    if not sport:
        raise HTTPException(status_code=404, detail="Sport not found")
    
    db_game = models.Game(**game.dict())
    db.add(db_game)
    db.commit()
    db.refresh(db_game)
    return db_game


@app.get("/games/{game_id}", response_model=schemas.GameStateResponse)
def get_game_state(game_id: int, db: Session = Depends(get_db)):
    """
    GET /games/{game_id}
    Get game metadata and play-by-play history.
    """
    game = db.query(models.Game).filter(models.Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    # Events are already loaded via relationship and ordered by created_at
    return game


@app.post("/games/{game_id}/events", response_model=schemas.EventResponse, status_code=201)
async def create_event(
    game_id: int,
    event: schemas.EventCreate,
    db: Session = Depends(get_db)
):
    """
    POST /games/{game_id}/events
    Create a new play-by-play event.
    """
    # Verify game exists
    game = db.query(models.Game).filter(models.Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    # Validate team is A or B (already validated in schema, but double-check)
    if event.team not in [models.TeamSide.A, models.TeamSide.B]:
        raise HTTPException(status_code=400, detail="Team must be A or B")
    
    # Create event
    db_event = models.PlayByPlayEvent(
        game_id=game_id,
        team=event.team,
        minute=event.minute,
        description=event.description
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    
    # Broadcast to WebSocket clients
    payload = schemas.WebSocketEventPayload(
        event_id=db_event.id,
        game_id=game_id,
        team=db_event.team.value,
        minute=db_event.minute,
        description=db_event.description,
        timestamp=db_event.created_at
    )
    await manager.broadcast(game_id, payload.dict())
    
    return db_event


# WebSocket Endpoint

@app.websocket("/ws/games/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: int):
    """
    WebSocket endpoint for real-time game updates.
    /ws/games/{game_id}
    """
    # Check origin for WebSocket connections (CORS doesn't apply to WebSockets)
    origin = websocket.headers.get("origin")
    allowed_origins = [
        "https://micho8cho93.github.io",
        "https://micho8cho93.github.io/scoreboard_frontend",
        "https://micho8cho93.github.io/scoreboard_frontend/",
    ]
    
    if origin and origin.rstrip('/') not in [o.rstrip('/') for o in allowed_origins]:
        await websocket.close(code=1008, reason="Origin not allowed")
        return
    
    # Verify game exists using a database session
    db = next(get_db())
    try:
        game = db.query(models.Game).filter(models.Game.id == game_id).first()
        if not game:
            await websocket.close(code=1008, reason="Game not found")
            return
        
        # Connect client
        await manager.connect(websocket, game_id)
        
        try:
            # Keep connection alive and handle any incoming messages
            while True:
                # Wait for messages (client can send ping/pong or other commands)
                # Use receive() instead of receive_text() to handle both text and ping/pong
                message = await websocket.receive()
                if message.get("type") == "websocket.disconnect":
                    break
                # For now, we just ignore client messages
                # In future, could handle commands like "ping"
        except WebSocketDisconnect:
            manager.disconnect(websocket, game_id)
        except Exception as e:
            manager.disconnect(websocket, game_id)
            print(f"WebSocket error: {e}")
    finally:
        db.close()


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Real-Time Scoreboard API",
        "version": "1.0.0",
        "docs": "/docs"
    }

