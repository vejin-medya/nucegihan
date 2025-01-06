import sqlite3

def create_tables():
    conn = sqlite3.connect('news.db')
    conn.execute("""
    CREATE TABLE IF NOT EXISTS news (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        link TEXT UNIQUE,
        headline TEXT,
        image_url TEXT,
        publish_date TEXT,
        site_name TEXT
    )
    """)
    conn.close()
