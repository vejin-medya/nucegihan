import sqlite3

class DatabaseManager:
    def __init__(self, db_name='news.db'):
        self.db_name = db_name

    def get_db_connection(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn

    def create_table(self):
        conn = self.get_db_connection()
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

    def save_news(self, data):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        for news in data:
            cursor.execute(
                """
                INSERT OR IGNORE INTO news (link, headline, image_url, publish_date, site_name)
                VALUES (?, ?, ?, ?, ?)
                """,
                (news['link'], news['headline'], news['image_url'], news['publish_date'], news['site_name'])
            )
        conn.commit()
        conn.close()

    def get_news(self, site=None, since=None):
        conn = self.get_db_connection()
        query = "SELECT * FROM news"
        params = []

        if site:
            query += " WHERE site_name = ?"
            params.append(site)
        if since:
            query += " AND publish_date > ?" if site else " WHERE publish_date > ?"
            params.append(since)

        query += " ORDER BY publish_date DESC LIMIT 200"
        news = conn.execute(query, params).fetchall()
        conn.close()
        return [dict(row) for row in news]
