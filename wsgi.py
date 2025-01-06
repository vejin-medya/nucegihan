from app.main import app
from app.newsFetcher import NewsFetcher
from app.scheduler import Scheduler

news_fetcher = NewsFetcher('news.db')

import os


if __name__ == '__main__':
    # # İlk scraping işlemleri
    # print("Starting initial scraping...")
    # diyarname_data = news_fetcher.diyarname_rss()
    # bianet_data = news_fetcher.fetch_bianet_rss()
    # ajansa_welat_data = news_fetcher.scrape_ajansa_welat()
    # xwebun_data = news_fetcher.scrape_xwebun()

    # nuhev_data = news_fetcher.fetch_rss('https://www.nuhev.com/feed/', 'Nuhev')

    # news_fetcher.save_news(diyarname_data + bianet_data + ajansa_welat_data + nuhev_data + xwebun_data)
    
    # # Zamanlayıcıyı başlat
    # scheduler = Scheduler(news_fetcher)
    # scheduler.setup_scheduler()
    
    # API'yi başlat
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)