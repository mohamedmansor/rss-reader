
from config import celery_app
from celery import chain, shared_task


@shared_task
def auto_refresh_followed_feeds():
    """
    Celery beat task that auto refreshes feed posts.
    """
    
    return
