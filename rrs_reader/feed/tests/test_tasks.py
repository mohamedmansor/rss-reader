from django.test import TestCase

from unittest.mock import patch

from django.core.exceptions import ObjectDoesNotExist

from unittest import mock
from celery.exceptions import MaxRetriesExceededError


from rrs_reader.feed.models import Feed
from rrs_reader.feed.exceptions import FeedException
from rrs_reader.feed.tasks import refresh_feed, periodic_update_feeds_task
from celery.result import AsyncResult

from rrs_reader.feed.tests.factories import FeedFactory



class PeriodicUpdateFeedsTaskTestCase(TestCase):
    def setUp(self):
        self.feeds = FeedFactory.create(auto_refresh=False)

    def test_periodic_update_feeds_task_no_feeds(self):
        result = periodic_update_feeds_task()
        self.assertEqual(result, "No Feeds to update")

class RefreshFeedTestCase(TestCase):
    @mock.patch("rrs_reader.feed.tasks.json.dumps")
    @mock.patch("rrs_reader.feed.tasks.NotificationService.notify")
    @mock.patch("rrs_reader.feed.tasks.logger.error")
    @mock.patch("rrs_reader.feed.tasks.refresh_feed.retry")
    @mock.patch("rrs_reader.feed.tasks.FeedService.update_feed")
    def test_refresh_feed_success(self, mock_update_feed, mock_retry, mock_logger, mock_notify, mock_dumps):
        feed_id = 1
        feed = Feed(id=feed_id)
        mock_get = mock.Mock(return_value=feed)
        with mock.patch("rrs_reader.feed.tasks.Feed.objects.get", mock_get):
            refresh_feed(feed_id)

        mock_get.assert_called_once_with(id=feed_id)
        mock_update_feed.assert_called_once_with()
        mock_dumps.assert_called_once_with({"detail": f"Updated Feed: [], Failed Feed: 0 "})

    @mock.patch("rrs_reader.feed.tasks.json.dumps")
    @mock.patch("rrs_reader.feed.tasks.NotificationService.notify")
    @mock.patch("rrs_reader.feed.tasks.logger.error")
    @mock.patch("rrs_reader.feed.tasks.refresh_feed.retry")
    @mock.patch("rrs_reader.feed.tasks.FeedService.update_feed")
    def test_refresh_feed_exception_retry(self, mock_update_feed, mock_retry, mock_logger, mock_notify, mock_dumps):
        feed_id = 1
        feed = Feed(id=feed_id)
        mock_get = mock.Mock(return_value=feed)
        with mock.patch("rrs_reader.feed.tasks.Feed.objects.get", mock_get):
            mock_update_feed.side_effect = FeedException
            refresh_feed(feed_id)

        mock_get.assert_called_once_with(id=feed_id)
        mock_update_feed.assert_called_once_with()
        mock_retry.assert_called_once_with()
        mock_dumps.assert_called_once_with({"detail": f"Updated Feed: [], Failed Feed: 0 "})

    @mock.patch("rrs_reader.feed.tasks.json.dumps")
    @mock.patch("rrs_reader.feed.tasks.NotificationService.notify")
    @mock.patch("rrs_reader.feed.tasks.logger.error")
    @mock.patch("rrs_reader.feed.tasks.refresh_feed.retry")
    @mock.patch("rrs_reader.feed.tasks.FeedService.update_feed")
    def test_refresh_feed_exception_max_retries_exceeded(self, mock_update_feed, mock_retry, mock_logger, mock_notify, mock_dumps):
        feed_id = 1
        feed = Feed(id=feed_id)
        mock_get = mock.Mock(return_value=feed)
        with mock.patch("rrs_reader.feed.tasks.Feed.objects.get", mock_get):
            mock_retry.side_effect = MaxRetriesExceededError
            refresh_feed(feed_id)

        mock_get.assert_called_once_with(id=feed_id)
        mock_update_feed.assert_called_once_with()
        mock_retry.assert_called_once_with()
        feed.deactivate_auto_refresh.assert_called_once_with()
        mock_notify.assert_called_once_with(
            user=feed.creator,
            subject="Feed has exceeded the max number of retries",
            message=f"Feed with id: {feed.id} has exceeded the max number of retries.",
        )
        mock_logger.assert_called_once_with(f"Updating feed with id: {feed.id} has exceeded the max number of retries. ")
        mock_dumps.assert_called_once_with({"detail": f"Updated Feed: [], Failed Feed: 0 "})

    @mock.patch("rrs_reader.feed.tasks.json.dumps")
    @mock.patch("rrs_reader.feed.tasks.NotificationService.notify")
    @mock.patch("rrs_reader.feed.tasks.logger.error")
    @mock.patch("rrs_reader.feed.tasks.refresh_feed.retry")
    @mock.patch("rrs_reader.feed.tasks.FeedService.update_feed")
    def test_refresh_feed_object_does_not_exist(self, mock_update_feed, mock_retry, mock_logger, mock_notify, mock_dumps):
        feed_id = 1
        mock_get = mock.Mock(side_effect=ObjectDoesNotExist)
        with mock.patch("rrs_reader.feed.tasks.Feed.objects.get", mock_get):
            refresh_feed(feed_id)

        mock_get.assert_called_once_with(id=feed_id)
        mock_update_feed.assert_not_called()
        mock_retry.assert_not_called()
        mock_logger.assert_not_called()
        mock_notify.assert_not_called()
        mock_dumps.assert_called_once_with({"detail": f"Updated Feed: [], Failed Feed: 0 "})
