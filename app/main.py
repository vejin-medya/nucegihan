from flask import Flask, request, jsonify, render_template
from app.newsFetcher import NewsFetcher
from app.database_manager import DatabaseManager, News
import os
from dotenv import load_dotenv
# Path setup
current_dir = os.path.dirname(os.path.abspath(__file__))
template_folder_path = os.path.join(current_dir, 'templates')  # Path to templates folder
app = Flask(__name__, template_folder=template_folder_path)

# Print the absolute path of the template folder for debugging (Remove this in production)
print("Template folder path:", os.path.abspath(app.template_folder))

load_dotenv()
db_url = os.getenv('DATABASE_URL')
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
db_manager = DatabaseManager(db_url)
# Initialize NewsFetcher
news_fetcher = NewsFetcher()

# Routes
@app.route('/save-news')
def save_news():
    try:
        diyarname_data = NewsFetcher.diyarname_rss()
        bianet_data = NewsFetcher.fetch_bianet_rss()
        ajansa_welat_data = NewsFetcher.scrape_ajansa_welat()
        xwebun_data = NewsFetcher.scrape_xwebun()
        nuhev_data = NewsFetcher.fetch_rss('https://www.nuhev.com/feed/', 'Nuhev')

        all_news = diyarname_data + bianet_data + ajansa_welat_data + xwebun_data + nuhev_data
        saved_count = db_manager.save_news(all_news)
        
        return {"message": "News fetched and saved successfully", "saved_count": saved_count}, 200

    except Exception as e:
        print(f"Error during scraping or saving: {e}")
        return {"message": "An error occurred", "error": str(e)}, 500

@app.route('/', methods=['GET'])
def nuce():
    news_data = (
        news_fetcher.diyarname_rss()
        + news_fetcher.fetch_bianet_rss()
        + news_fetcher.scrape_ajansa_welat()
        + news_fetcher.scrape_xwebun()
        + news_fetcher.fetch_rss('https://www.nuhev.com/feed/', 'Nuhev')
    )
    return render_template('news_list.html', news=news_data)
@app.route('/all-news', methods=['GET'])
def all_news():
    site = request.args.get('site')
    since = request.args.get('since')
    news_items = db_manager.get_news(site, since)
    # Serialize the results
    news_list = [{
        'id': news["id"],
        'link': news["link"],
        'headline': news["headline"],
        'image_url': news["image_url"],
        'publish_date': news["publish_date"],
        'site_name': news["site_name"]
    } for news in news_items]
    return render_template('news_list.html', news=news_list)