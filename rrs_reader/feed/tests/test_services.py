from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from rrs_reader.feed.models import Feed, Post
from rrs_reader.feed.services import FeedService
from rrs_reader.feed.tests.factories import FeedFactory, PostFactory


class FeedServiceTestCase(TestCase):
    def setUp(self):
        self.feed = FeedFactory.create(xml_url="https://example.com/feed.xml")

    def test_parse_rrs_link(self):
        # Mock the feedparser.parse method to return a sample parsed data
        with patch("rrs_reader.feed.services.feedparser.parse") as mock_parse:
            mock_parse.return_value = {
                "feed": {
                    "title": "Example Feed",
                    "link": "https://example.com",
                    "subtitle": "This is an example feed",
                },
                "entries": [
                    {
                        "title": "Post 1",
                        "summary": "This is the summary of post 1",
                        "link": "https://example.com/post1",
                        "published": "2022-01-01T12:00:00Z",
                    },
                    {
                        "title": "Post 2",
                        "summary": "This is the summary of post 2",
                        "link": "https://example.com/post2",
                        "published": "2022-01-02T12:00:00Z",
                    },
                ],
            }

            feed_service = FeedService(self.feed)
            parsed_data = feed_service.parse_rrs_link()

            self.assertEqual(parsed_data["feed"]["title"], "Example Feed")
            self.assertEqual(parsed_data["entries"][0]["title"], "Post 1")
            self.assertEqual(parsed_data["entries"][1]["title"], "Post 2")

    def test_prepare_feed_fields(self):
        feed_service = FeedService(self.feed)
        feed_dict = {"title": "Example Feed", "link": "https://example.com", "subtitle": "This is an example feed"}

        fields = feed_service._prepare_feed_fields(feed_dict)

        self.assertEqual(fields["title"], "Example Feed")
        self.assertEqual(fields["link"], "https://example.com")
        self.assertEqual(fields["description"], "This is an example feed")

    def test_prepare_post_fields(self):
        feed_service = FeedService(self.feed)
        post_entity = {
            "title": "Post 1",
            "summary": "This is the summary of post 1",
            "link": "https://example.com/post1",
            "published": "2022-01-01T12:00:00Z",
        }

        fields = feed_service._prepare_post_fields(post_entity)

        self.assertEqual(fields["title"], "Post 1")
        self.assertEqual(fields["description"], "This is the summary of post 1")
        self.assertEqual(fields["link"], "https://example.com/post1")
        self.assertEqual(fields["published_time"], timezone.datetime(2022, 1, 1, 12, 0, 0, tzinfo=timezone.utc))

    def test_update_feed(self):
        # Mock the feedparser.parse method to return a sample parsed data
        with patch("rrs_reader.feed.services.feedparser.parse") as mock_parse:
            mock_parse.return_value = {
                "feed": {
                    "title": "Example Feed",
                    "link": "https://example.com",
                    "subtitle": "This is an example feed",
                },
                "entries": [
                    {
                        "title": "Post 1",
                        "summary": "This is the summary of post 1",
                        "link": "https://example.com/post1",
                        "published": "2022-01-01T12:00:00Z",
                    },
                    {
                        "title": "Post 2",
                        "summary": "This is the summary of post 2",
                        "link": "https://example.com/post2",
                        "published": "2022-01-02T12:00:00Z",
                    },
                ],
            }

            feed_service = FeedService(self.feed)
            count = feed_service.update_feed()

            # Check if the feed object is updated
            self.assertEqual(self.feed.title, "Example Feed")
            self.assertEqual(self.feed.link, "https://example.com")
            self.assertIsNotNone(self.feed.last_update)

            # Check if the posts are created or updated
            posts = Post.objects.filter(feed=self.feed)
            self.assertEqual(posts.count(), 2)

            post1 = posts.get(title="Post 1")
            post2 = posts.get(title="Post 2")

            self.assertEqual(post1.description, "This is the summary of post 1")
            self.assertEqual(post1.link, "https://example.com/post1")
            self.assertIsNotNone(post1.published_time)

            self.assertEqual(post2.description, "This is the summary of post 2")
            self.assertEqual(post2.link, "https://example.com/post2")
            self.assertIsNotNone(post2.published_time)

            # Check if the count of newly created posts is correct
            self.assertEqual(count, 2)
