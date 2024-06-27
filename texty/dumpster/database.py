
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional

from texty.gametypes import GameRow, GameState

DATABASE_FILE = "texty.db"

def initialize_db():
    """Initialize the database tables."""
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS games (
                id TEXT PRIMARY KEY,
                state TEXT NOT NULL,
                created TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id TEXT NOT NULL,
                message TEXT NOT NULL,
                response TEXT NOT NULL,
                FOREIGN KEY (game_id) REFERENCES games (id)
            )
        ''')
        conn.commit()

def save_game_state(game_id: str, state: GameState):
    """Save the game state with the given game ID."""
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        now = datetime.utcnow().isoformat()
        cursor.execute('''
            INSERT OR REPLACE INTO games (id, state, updated)
            VALUES (?, ?, ?)
        ''', (game_id, state.model_dump_json(), now))
        conn.commit()

def load_game_state(game_id: str) -> GameState:
    """Load the game state by game ID."""
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT state FROM games WHERE id = ?
        ''', (game_id,))
        row = cursor.fetchone()
        return json.loads(row[0]) if row else None

def last_game() -> Optional[GameRow]:
    """Get the last played game"""
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, state, created, updated FROM games ORDER BY updated DESC LIMIT 1
        ''')
        row = cursor.fetchone()
        return GameRow(id=row[0], state=row[1], created=row[2], updated=row[3]) if row else None

def list_games() -> List[GameRow]:
    """List all game IDs along with the games description and the last updated date"""
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, state, created, updated FROM games
        ''')
        rows = cursor.fetchall()
        return [GameRow(id=row[0], state=row[1], created=row[2], updated=row[3]) for row in rows]

def log_message_response(game_id: str, message: str, response: str):
    """Log the LLM message and response."""
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO logs (game_id, message, response)
            VALUES (?, ?, ?)
        ''', (game_id, message, response))
        conn.commit()
