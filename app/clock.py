from apscheduler.schedulers.blocking import BlockingScheduler
from app.newsFetcher import NewsFetcher
sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=10)
def timed_job():
    NewsFetcher.fetch_and_save_allNews()
    print('This job is run every three minutes')

sched.start()