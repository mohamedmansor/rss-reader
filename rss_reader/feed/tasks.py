import json
import logging

from celery import group, shared_task
from celery.exceptions import MaxRetriesExceededError
from django.conf import settings

from rss_reader.feed.exceptions import FeedException
from rss_reader.feed.models import Feed
from rss_reader.feed.services import FeedService, NotificationService

logger = logging.getLogger(__name__)


@shared_task
def periodic_update_feeds_task():
    """
    Celery beat task that updates feeds.
    """

    feeds = Feed.objects.filter(followers__isnull=False, auto_refresh=True).values_list("id", flat=True)
    if not feeds:
        return "No Feeds to update"
    # Groupping them to get use of celery async options.
    group(refresh_feed.s(feed_id) for feed_id in feeds).apply_async()


@shared_task(
    autoretry_for=(FeedException,),
    retry_kwargs={"max_retries": settings.MAX_RETRY_FEED_UPDATES},
    retry_backoff=settings.RETRY_BACKOFF_IN_SECONDS,
    retry_backoff_max=settings.RETRY_BACKOFF_MAX,
)
def refresh_feed(feed_id):
    updated_feed_ids = []
    failed_feed_ids = []
    feed = Feed.objects.get(id=feed_id)
    try:
        feed_svc = FeedService(feed)
        feed_svc.update_feed()
        updated_feed_ids.append(feed_id)
    except FeedException:
        try:
            refresh_feed.retry()
        except MaxRetriesExceededError:
            feed.deactivate_auto_refresh()
            failed_feed_ids.append(feed_id)
            NotificationService.notify(
                user=feed.creator,
                subject="Feed has exceeded the max number of retries",
                message=f"Feed with id: {feed.id} has exceeded the max number of retries.",
            )
            logger.error(f"Updating feed with id: {feed.id} has exceeded the max number of retries. ")
    return json.dumps({"detail": f"Updated Feed: {updated_feed_ids}, Failed Feed: {len(failed_feed_ids)} "})
