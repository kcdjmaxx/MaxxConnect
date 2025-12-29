# CeleryApp
**Source Spec:** phase-2-campaign-management.md

## Responsibilities
### Knows
- broker_url: Redis connection URL
- result_backend: Redis URL for task results
- task_queues: Named queues (email_queue, sms_queue)
- concurrency: Number of worker processes

### Does
- configure(): Set up Celery with Redis broker
- register_tasks(): Register email and SMS tasks
- start_workers(): Launch worker processes
- get_task_status(task_id): Query task state
- revoke_task(task_id): Cancel pending task
- get_queue_length(queue_name): Return pending task count

## Collaborators
- EmailQueueTask: Registered Celery task for email
- SMSQueueTask: Registered Celery task for SMS
- RateLimiter: Rate limiting integration

## Sequences
- seq-campaign-send.md: Task queuing and processing
