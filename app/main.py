from flask import Flask, request, jsonify,render_template
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

@app.route('/', methods=['GET'])
def nuce():
    diyarname_data = news_fetcher.diyarname_rss()
    bianet_data = news_fetcher.fetch_bianet_rss()
    ajansa_welat_data = news_fetcher.scrape_ajansa_welat()
    xwebun_data = news_fetcher.scrape_xwebun()

    nuhev_data = news_fetcher.fetch_rss('https://www.nuhev.com/feed/', 'Nuhev')
    news_data = diyarname_data + bianet_data + ajansa_welat_data + nuhev_data + xwebun_data
    return render_template('news_list.html', news=news_data)
    