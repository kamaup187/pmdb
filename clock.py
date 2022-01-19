from apscheduler.schedulers.blocking import BlockingScheduler
import requests

sched = BlockingScheduler()

@sched.scheduled_job('interval', seconds=3)
def timed_job():
    print('This job is run every three seconds.')
    # r =requests.get('https://kiotapay.com/index')

# @sched.scheduled_job('cron', day_of_week='mon-sun', hour=22,minute=22)
# def scheduled_job():
#     print('This job is run every weekday at 5pm.')

sched.start()
