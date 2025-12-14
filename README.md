# Real-Time Scoreboard Application

A live play-by-play scoreboard application supporting multiple sports and games, with real-time WebSocket updates.

## Architecture

- **Backend**: FastAPI with WebSocket support
- **Frontend**: Static HTML/CSS/JavaScript (deployable to GitHub Pages or Vercel)
- **Database**: SQLite (development) / PostgreSQL (production)

## Features

- Multiple sports support
- Multiple games per sport
- Real-time play-by-play event updates via WebSocket
- RESTful API for managing sports, games, and events
- Responsive frontend with live scoreboard

## Setup

### Prerequisites

- Python 3.8+
- pip

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Initialize the database:
```bash
python -c "from app.database import init_db; init_db()"
```

3. Run the backend server:
```bash
python run.py
```

The API will be available at `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### Frontend

Open `frontend/index.html` in a browser, or serve it with a static file server:

```bash
cd frontend
python -m http.server 3000
```

Then open `http://localhost:3000` in your browser.

**Note**: Update `API_BASE_URL` in `frontend/app.js` if your backend is running on a different host/port.

## API Endpoints

### REST Endpoints

- `GET /sports` - List all sports
- `POST /sports` - Create a new sport
- `GET /sports/{sport_id}/games` - List games for a sport
- `POST /games` - Create a new game
- `GET /games/{game_id}` - Get game metadata and play-by-play history
- `POST /games/{game_id}/events` - Create a new play-by-play event

### WebSocket

- `WS /ws/games/{game_id}` - Real-time event updates for a game

## Testing

Run all tests:
```bash
pytest
```

Run tests by phase:
```bash
# Phase 1: Domain Models
pytest tests/test_models.py

# Phase 2: REST API
pytest tests/test_api.py

# Phase 3: Events API
pytest tests/test_events.py

# Phase 4: WebSocket
pytest tests/test_websocket.py

# Phase 5: Integration
pytest tests/test_integration.py
```

## Project Structure

```
scoreboard/
├── app/                    # Backend application
│   ├── __init__.py
│   ├── main.py            # FastAPI app and routes
│   ├── models.py          # SQLAlchemy models
│   ├── schemas.py         # Pydantic schemas
│   └── database.py       # Database configuration
├── frontend/              # Frontend application
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── tests/                 # Test suite
│   ├── test_models.py     # Phase 1: Domain models
│   ├── test_api.py        # Phase 2: REST API
│   ├── test_events.py     # Phase 3: Events API
│   ├── test_websocket.py  # Phase 4: WebSocket
│   ├── test_integration.py # Phase 5: Integration
│   ├── test_frontend.py   # Phase 6: Frontend
│   └── test_e2e.py        # Phase 7: E2E
├── requirements.txt
├── pytest.ini
├── run.py                 # Development server
└── README.md
```

## Usage Example

1. **Create a sport**:
```bash
curl -X POST "http://localhost:8000/sports" \
  -H "Content-Type: application/json" \
  -d '{"name": "Soccer", "slug": "soccer"}'
```

2. **Create a game**:
```bash
curl -X POST "http://localhost:8000/games" \
  -H "Content-Type: application/json" \
  -d '{"sport_id": 1, "team_a_name": "Team A", "team_b_name": "Team B"}'
```

3. **Add an event**:
```bash
curl -X POST "http://localhost:8000/games/1/events" \
  -H "Content-Type: application/json" \
  -d '{"team": "A", "minute": 10, "description": "Goal!"}'
```

4. **View game state**:
```bash
curl "http://localhost:8000/games/1"
```

## Deployment

### Backend

Deploy to any platform supporting FastAPI (Heroku, Railway, Render, etc.):

1. Set `DATABASE_URL` environment variable (for PostgreSQL)
2. Run database migrations
3. Deploy the application

### Frontend

Deploy to GitHub Pages or Vercel:

1. Update `API_BASE_URL` in `frontend/app.js` to point to your backend
2. Deploy the `frontend/` directory

## Development

The project follows Test-Driven Development (TDD) principles. See `test_roadmap.yml` for the complete test plan.

## License

MIT

