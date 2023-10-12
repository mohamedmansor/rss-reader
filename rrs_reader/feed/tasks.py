import logging

from config import celery_app
from celery import group, shared_task
from celery.exceptions import MaxRetriesExceededError


logger = logging.getLogger(__name__)


@shared_task
def auto_refresh_followed_feeds():
    """
    Celery beat task that auto refreshes feed posts.
    """

    return
