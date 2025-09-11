"""
Celery application for background processing and async tasks
Production-ready configuration with Redis backend
"""
import os
from celery import Celery
from celery.schedules import crontab

# Redis configuration from environment
redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

def make_celery(app_name=__name__):
    """Create Celery app with Flask integration"""
    broker_url = redis_url
    result_backend = redis_url
    
    celery = Celery(
        app_name,
        broker=broker_url,
        backend=result_backend,
        include=[
            'tasks.broker_tasks',
            'tasks.market_data_tasks', 
            'tasks.ai_analysis_tasks',
            'tasks.notification_tasks'
        ]
    )
    
    # Production-ready configuration
    celery.conf.update(
        # Task execution
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        
        # Worker configuration
        worker_max_tasks_per_child=1000,  # Prevent memory leaks
        worker_disable_rate_limits=False,
        worker_prefetch_multiplier=1,      # One task at a time for reliability
        
        # Result backend settings
        result_expires=3600,               # Results expire after 1 hour
        result_persistent=True,
        
        # Task routing and priorities
        task_routes={
            'tasks.broker_tasks.*': {'queue': 'broker_operations'},
            'tasks.market_data_tasks.*': {'queue': 'market_data'},
            'tasks.ai_analysis_tasks.*': {'queue': 'ai_analysis'},
            'tasks.notification_tasks.*': {'queue': 'notifications'},
        },
        
        # Error handling
        task_acks_late=True,
        task_reject_on_worker_lost=True,
        
        # Monitoring
        worker_send_task_events=True,
        task_send_sent_event=True,
        
        # Beat scheduler configuration
        beat_schedule={
            'sync-broker-data': {
                'task': 'tasks.broker_tasks.sync_all_broker_data',
                'schedule': crontab(minute='*/5'),  # Every 5 minutes
            },
            'update-market-data': {
                'task': 'tasks.market_data_tasks.update_market_indices', 
                'schedule': crontab(minute='*/2'),  # Every 2 minutes
            },
            'cleanup-expired-sessions': {
                'task': 'tasks.maintenance_tasks.cleanup_expired_sessions',
                'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
            },
        },
    )
    
    return celery

# Create the Celery instance
celery_app = make_celery()

if __name__ == '__main__':
    celery_app.start()