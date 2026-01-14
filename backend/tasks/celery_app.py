"""
Celery Configuration - Background task queue setup

CRC: crc-CeleryApp.md
Seq: seq-email-process.md, seq-sms-process.md
"""
from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

# Redis URL from environment (Railway provides this automatically)
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Create Celery app
celery_app = Celery(
    'maxxconnect',
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=['backend.tasks.email_task', 'backend.tasks.sms_task']
)

# Configuration
celery_app.conf.update(
    # Task result expiration (24 hours)
    result_expires=86400,

    # Task acknowledgment: late ack means task stays in queue until complete
    task_acks_late=True,

    # Prefetch only 1 task at a time (important for rate limiting)
    worker_prefetch_multiplier=1,

    # Task serialization
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',

    # Timezone
    timezone='America/Chicago',

    # Task routing - separate queues for email and SMS
    task_routes={
        'backend.tasks.email_task.*': {'queue': 'email_queue'},
        'backend.tasks.sms_task.*': {'queue': 'sms_queue'},
    },

    # Default retry settings
    task_default_retry_delay=2,
    task_max_retries=3,
)


def get_task_status(task_id):
    """Get status of a task by ID"""
    from celery.result import AsyncResult
    result = AsyncResult(task_id, app=celery_app)
    return {
        'task_id': task_id,
        'status': result.status,
        'result': result.result if result.ready() else None
    }


def get_queue_length(queue_name='celery'):
    """Get approximate number of tasks in queue"""
    try:
        with celery_app.pool.acquire(block=True) as conn:
            return conn.default_channel.client.llen(queue_name)
    except Exception:
        return 0
