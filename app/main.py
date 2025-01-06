from flask import Flask, request, jsonify
from app.newsFetcher import NewsFetcher
from app.scheduler import Scheduler
from app.models import create_tables

# Flask API
app = Flask(__name__)

# Veritabanı ve haber çekme sınıfı
news_fetcher = NewsFetcher('news.db')

# Veritabanı tablolarını oluştur
create_tables()

# API Endpoint'leri
@app.route('/news', methods=['GET'])
def get_news():
    site = request.args.get('site')
    since = request.args.get('since')

    conn = news_fetcher.get_db_connection()
    query = "SELECT * FROM news"
    params = []

    if site:
        query += " WHERE site_name = ?"
        params.append(site)
    if since:
        query += " AND publish_date > ?" if site else " WHERE publish_date > ?"
        params.append(since)
    query += " ORDER BY publish_date DESC LIMIT 300"
    news = conn.execute(query, params).fetchall()
    conn.close()
    return jsonify([dict(row) for row in news])