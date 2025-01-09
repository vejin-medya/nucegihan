import os
from app.main import app
from app.newsFetcher import NewsFetcher

if __name__ == '__main__':
    NewsFetcher.fetch_and_save_allNews()
    # Run the Flask app
    port = int(os.getenv("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)