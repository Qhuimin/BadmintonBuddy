import sqlite3
import os
from game import Game

DB_NAME = "badminton_buddy.db"

def init_db():
    """Initializes the SQLite database and creates the games table if it doesn't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            venue TEXT NOT NULL,
            level TEXT,
            start_time TEXT,
            end_time TEXT,
            price TEXT,
            original_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(date, venue, start_time, end_time)
        )
    """)
    
    conn.commit()
    conn.close()

def save_games(games: list[Game]) -> int:
    """
    Inserts a list of parsed Game objects into the database.
    Returns the count of *newly* inserted unique games.
    """
    if not games:
        return 0
        
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    new_games_count = 0
    
    for game in games:
        try:
            cursor.execute("""
                INSERT INTO games (date, venue, level, start_time, end_time, price, original_message)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (game.date, game.venue, game.level, game.start_time, game.end_time, game.price, game.original_message))
            new_games_count += 1
        except sqlite3.IntegrityError:
            # Enters here if the UNIQUE constraint fails (meaning the game already exists)
            continue
            
    conn.commit()
    conn.close()
    return new_games_count


def get_filtered_games(venue_keyword: str = None, max_price: float = None) -> list[dict]:
    """
    Retrieves saved games from the database based on search preferences.
    Returns a list of dictionaries for easier rendering.
    """
    conn = sqlite3.connect(DB_NAME)
    # Allows fetching rows as dictionaries instead of raw tuples
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    
    query = "SELECT * FROM games WHERE 1=1"
    params = []
    
    # 1. Location Filter (e.g., "Bedok" or "Tampines")
    if venue_keyword:
        query += " AND venue LIKE ?"
        params.append(f"%{venue_keyword}%")
        
    # 2. Budget Filter (e.g., skips slots more expensive than $15)
    if max_price is not None:
        # Simple extraction logic: strips '$' and casts temporarily in SQL if possible,
        # or handles rough evaluation. For scaling, we match numerical patterns.
        query += " AND CAST(REPLACE(REPLACE(price, '$', ''), ' ', '') AS REAL) <= ?"
        params.append(max_price)
        
    # Order by newest discovered games first
    query += " ORDER BY id DESC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]