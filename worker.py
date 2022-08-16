import os

import redis
from rq import Worker, Queue, Connection

listen = ['default']

redis_url = os.getenv('REDISTOGO_URL')
if not redis_url:
    print("THIS IS THE NORMAL REDIS_URL >>>>",redis_url)

    redis_url = os.getenv('REDIS_URL')

print("THIS IS THE FINAL REDIS_URL >>>>",redis_url)

if not redis_url:
    redis_url = "redis://localhost:6379"

conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(list(map(Queue, listen)))
        worker.work(with_scheduler=True)
