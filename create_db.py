import sqlite3
from pathlib import Path

def create_database():
    """Create SQLite database with user query history table"""
    db_path = Path("math_bot.db")
    
    if db_path.exists():
        print("Database already exists")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS query_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        username TEXT,
        query TEXT NOT NULL,
        result TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Create index for faster user-specific queries
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON query_history(user_id)")
    
    conn.commit()
    conn.close()
    print("Database created successfully")

if __name__ == "__main__":
    create_database()