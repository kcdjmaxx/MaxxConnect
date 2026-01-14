web: gunicorn app:app
worker: celery -A backend.tasks.celery_app worker --loglevel=info --concurrency=2
