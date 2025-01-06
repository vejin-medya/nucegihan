from apscheduler.schedulers.background import BackgroundScheduler


class Scheduler:
    def __init__(self, fetcher):
        self.fetcher = fetcher

    def setup_scheduler(self):
        scheduler = BackgroundScheduler()

        # RSS siteleri
        scheduler.add_job(lambda: self.fetcher.fetch_rss('https://bianet.org/rss', 'Bianet'), 'cron', hour=12)
        scheduler.add_job(lambda: self.fetcher.fetch_rss('https://nuhev.com/rss', 'Nuhev'), 'cron', hour=21)
        scheduler.add_job(lambda: self.fetcher.diyarname_rss(), 'cron', hour=12)

        # Scraping siteleri
        scheduler.add_job(self.fetcher.scrape_ajansa_welat, 'interval', hours=5)
        scheduler.add_job(self.fetcher.scrape_xwebun, 'interval', hours=5)

        scheduler.start()
