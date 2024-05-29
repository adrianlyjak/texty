
import sqlite3
import json
from typing import List, Dict

DATABASE_FILE = "texty.db"

def initialize_db():
    """Initialize the database tables."""
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS games (
                id TEXT PRIMARY KEY,
                state TEXT NOT NULL
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

def save_game_state(game_id: str, state: Dict):
    """Save the game state with the given game ID."""
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO games (id, state)
            VALUES (?, ?)
        ''', (game_id, json.dumps(state)))
        conn.commit()

def load_game_state(game_id: str) -> Dict:
    """Load the game state by game ID."""
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT state FROM games WHERE id = ?
        ''', (game_id,))
        row = cursor.fetchone()
        return json.loads(row[0]) if row else None

def list_game_ids() -> List[str]:
    """List all game IDs."""
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id FROM games
        ''')
        rows = cursor.fetchall()
        return [row[0] for row in rows]

def log_message_response(game_id: str, message: str, response: str):
    """Log the LLM message and response."""
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO logs (game_id, message, response)
            VALUES (?, ?, ?)
        ''', (game_id, message, response))
        conn.commit()
