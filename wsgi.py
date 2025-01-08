import os
from app.main import app
from app.newsFetcher import NewsFetcher
from app.database_manager import DatabaseManager
from dotenv import load_dotenv
from app.scheduler import Scheduler


load_dotenv()
db_url = os.getenv('DATABASE_URL')
print(db_url)
if not db_url:
    raise ValueError("DATABASE_URL is not set in the environment variables.")

db_manager = DatabaseManager(db_url)
if __name__ == '__main__':
    NewsFetcher.fetch_and_save_allNews()
    # Zamanlayıcıyı başlat
    scheduler = Scheduler(NewsFetcher)
    scheduler.setup_scheduler()
    # Run the Flask app
    port = int(os.getenv("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)