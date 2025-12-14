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
        connection_count = len(self.active_connections[game_id])
        print(f"✅ WebSocket client connected for game {game_id}")
        print(f"   Total connections for this game: {connection_count}")
        print(f"   All active games: {list(self.active_connections.keys())}")
    
    def disconnect(self, websocket: WebSocket, game_id: int):
        """Disconnect a client from a game's WebSocket."""
        if game_id in self.active_connections:
            if websocket in self.active_connections[game_id]:
                self.active_connections[game_id].remove(websocket)
                print(f"🔌 Client disconnected from game {game_id}")
            if not self.active_connections[game_id]:
                del self.active_connections[game_id]
                print(f"   No more connections for game {game_id}")
            else:
                print(f"   Remaining connections for game {game_id}: {len(self.active_connections[game_id])}")
    
    async def broadcast(self, game_id: int, message: dict):
        """Broadcast a message to all connected clients for a game."""
        print(f"\n{'='*50}")
        print(f"BROADCAST ATTEMPT for game {game_id}")
        print(f"Message: {message}")
        print(f"Active games: {list(self.active_connections.keys())}")
        
        if game_id in self.active_connections:
            connections = self.active_connections[game_id]
            print(f"Broadcasting to {len(connections)} clients")
            
            disconnected = []
            for i, connection in enumerate(connections):
                try:
                    await connection.send_json(message)
                    print(f"✅ Sent to client {i+1}/{len(connections)}")
                except Exception as e:
                    print(f"❌ Failed to send to client {i+1}: {e}")
                    disconnected.append(connection)
            
            for conn in disconnected:
                self.disconnect(conn, game_id)
            
            print(f"Broadcast complete. Disconnected: {len(disconnected)}")
        else:
            print(f"❌ NO ACTIVE CONNECTIONS for game {game_id}")
            print(f"Available games with connections: {list(self.active_connections.keys())}")
        print(f"{'='*50}\n")


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
    print(f"\n{'='*60}")
    print(f"CREATE EVENT CALLED")
    print(f"Game ID: {game_id}")
    print(f"Event data: {event.dict()}")
    print(f"Current manager state: {dict(manager.active_connections)}")
    print(f"{'='*60}\n")
    
    # Verify game exists
    game = db.query(models.Game).filter(models.Game.id == game_id).first()
    if not game:
        print(f"❌ Game {game_id} not found in database")
        raise HTTPException(status_code=404, detail="Game not found")
    
    print(f"✅ Game found: {game.team_a_name} vs {game.team_b_name}")
    
    # Validate team is A or B
    if event.team not in [models.TeamSide.A, models.TeamSide.B]:
        print(f"❌ Invalid team: {event.team}")
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
    
    print(f"✅ Event created with ID: {db_event.id}")
    
    # Broadcast to WebSocket clients
    payload = schemas.WebSocketEventPayload(
        event_id=db_event.id,
        game_id=game_id,
        team=db_event.team.value,
        minute=db_event.minute,
        description=db_event.description,
        timestamp=db_event.created_at
    )
    
    print(f"📡 Broadcasting payload: {payload.dict()}")
    await manager.broadcast(game_id, payload.dict())
    
    print(f"\n{'='*60}")
    print(f"EVENT CREATION COMPLETE")
    print(f"{'='*60}\n")
    
    return db_event


# WebSocket Endpoint

@app.websocket("/ws/games/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: int):
    """
    WebSocket endpoint for real-time game updates.
    /ws/games/{game_id}
    """
    origin = websocket.headers.get("origin")
    allowed_origins = [
        "https://micho8cho93.github.io",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        None
    ]
    
    print(f"\n{'='*60}")
    print(f"WEBSOCKET CONNECTION ATTEMPT")
    print(f"Game ID: {game_id}")
    print(f"Origin: {origin}")
    print(f"All headers: {dict(websocket.headers)}")
    print(f"{'='*60}\n")
    
    # More permissive origin check
    if origin:
        origin_normalized = origin.rstrip('/')
        allowed_normalized = [o.rstrip('/') if o else None for o in allowed_origins]
        if origin_normalized not in allowed_normalized:
            print(f"❌ Origin not allowed: {origin}")
            print(f"   Allowed origins: {allowed_origins}")
            await websocket.close(code=1008, reason="Origin not allowed")
            return
        else:
            print(f"✅ Origin allowed: {origin}")
    
    # Verify game exists
    db = next(get_db())
    try:
        game = db.query(models.Game).filter(models.Game.id == game_id).first()
        if not game:
            print(f"❌ Game {game_id} not found in database")
            await websocket.close(code=1008, reason="Game not found")
            return
        
        print(f"✅ Game found: {game.team_a_name} vs {game.team_b_name}")
        
        # Connect client
        await manager.connect(websocket, game_id)
        
        try:
            # Send initial connection confirmation
            await websocket.send_json({
                "type": "connection_established",
                "game_id": game_id,
                "message": "Connected to live updates"
            })
            print(f"✅ Sent connection confirmation to client")
            
            # Keep connection alive with periodic pings
            import asyncio
            last_ping = asyncio.get_event_loop().time()
            
            while True:
                try:
                    # Wait for messages with a timeout
                    data = await asyncio.wait_for(
                        websocket.receive_text(),
                        timeout=30.0
                    )
                    
                    print(f"📨 Received from client (game {game_id}): {data}")
                    
                    # Echo back for ping/pong
                    if data == "ping":
                        await websocket.send_text("pong")
                        print(f"   Sent pong response")
                        last_ping = asyncio.get_event_loop().time()
                        
                except asyncio.TimeoutError:
                    # Send keepalive ping to client
                    current_time = asyncio.get_event_loop().time()
                    if current_time - last_ping > 25:
                        try:
                            await websocket.send_json({
                                "type": "keepalive",
                                "timestamp": current_time
                            })
                            print(f"📡 Sent keepalive to game {game_id}")
                            last_ping = current_time
                        except Exception as e:
                            print(f"❌ Keepalive failed: {e}")
                            break
                    continue
                    
        except WebSocketDisconnect:
            print(f"🔌 WebSocket disconnected normally for game {game_id}")
        except Exception as e:
            print(f"❌ WebSocket error for game {game_id}: {type(e).__name__}: {e}")
        finally:
            manager.disconnect(websocket, game_id)
            print(f"🧹 Cleaned up connection for game {game_id}")
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

