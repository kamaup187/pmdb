##############################################################################
from rq import Queue
from rq.job import Job
from worker import conn

q = Queue(connection=conn)

from app.v1.views.helperfuncs import mbogi

from datetime import timedelta
import time

from rq.registry import ScheduledJobRegistry

# job = q.enqueue_at( datetime.datetime(2021, 1, 26, 22, 57), mbogi)
# job = mbog.enqueue_in(timedelta(seconds=10), mbogi)

registry = ScheduledJobRegistry(queue=q)
time.sleep(0.1)
print('Number of jobs in registry before scheduling %s' % registry.count)

if not registry.get_job_ids():
    print("passing job")
    job = q.enqueue_in(timedelta(seconds=10), mbogi)
else:
    print("job exists already")

for job_id in registry.get_job_ids():
    print('Number of jobs in registry after initial schedule %s' % registry.count)
    if registry.count < 1:
        # registry.remove(job_id, delete_job=True)
        job = q.enqueue_in(timedelta(seconds=10), mbogi)
        print('Number of jobs in registry after scheduling %s' % registry.count)
##############################################################################