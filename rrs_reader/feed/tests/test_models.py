from rrs_reader.feed.models import Feed, Post, UserFeed
from django.test import TestCase
from rrs_reader.feed.tests.factories import FeedFactory, UserFeedFactory, PostFactory
from rrs_reader.users.tests.factories import UserFactory

from django.core.exceptions import ValidationError


class TestFeedModel(TestCase):
    def setUp(self):
        self.user = UserFactory.create()
        self.feed = FeedFactory.create(
            creator=self.user,
            title="Test Feed",
            description="Test Description",
            xml_url="https://example.com/feed.xml",
            auto_refresh=True,
        )

    def test_deactivate_auto_refresh(self):
        self.feed.deactivate_auto_refresh()
        self.assertFalse(self.feed.auto_refresh)

    def test_activate_auto_refresh(self):
        self.feed.activate_auto_refresh()
        self.assertTrue(self.feed.auto_refresh)

    def test_is_followed_by_user(self):
        self.assertFalse(self.feed.is_followed_by_user(self.user))
        UserFeedFactory.create(user=self.user, feed=self.feed)
        self.assertTrue(self.feed.is_followed_by_user(self.user))

    def test_follow(self):
        self.feed.follow(self.user)
        user_feed = UserFeed.objects.filter(user=self.user, feed=self.feed).last()
        self.assertIsNotNone(user_feed)
        self.assertEqual(user_feed.feed, self.feed)

    def test_follow_followed_feed_raises_error(self):
        self.feed.follow(self.user)
        with self.assertRaises(ValidationError):
            self.feed.follow(self.user)

    def test_unfollow(self):
        UserFeedFactory.create(user=self.user, feed=self.feed)
        self.feed.unfollow(self.user)
        self.assertFalse(UserFeed.objects.filter(user=self.user, feed=self.feed).exists())


class TestPostModel(TestCase):
    def setUp(self):
        self.user = UserFactory.create(username='testuser', password='testpassword')
        self.feed = FeedFactory.create(
            creator=self.user,
            title='Test Feed',
            description='Test Description',
            xml_url='https://example.com/feed.xml',
            auto_refresh=True
        )
        self.post = PostFactory.create(
            feed=self.feed,
            title='Test Post',
            description='Test Description',
            link='https://example.com/post',
            published_time=None,
            last_update=None
        )
        self.user_feed = UserFeedFactory.create(user=self.user, feed=self.feed)
        # self.user_feed.read_posts.add(self.post)
        # self.user_feed.save()

    def test_mark_as_read(self):
        self.post.mark_as_read(self.user)
        self.assertTrue(self.post in self.user_feed.read_posts.all())
    
    def test_mark_read_post_as_read_raises_error(self):
        self.post.mark_as_read(self.user)
        with self.assertRaises(ValidationError):
            self.post.mark_as_read(self.user)

    def test_mark_as_unread(self):
        self.post.mark_as_read(self.user)
        self.post.mark_as_unread(self.user)
        self.assertFalse(self.post in self.user_feed.read_posts.all())

    def test_mark_unread_post_as_unread_raises_error(self):
        with self.assertRaises(ValidationError):
            self.post.mark_as_unread(self.user)

    def test_mark_all_read(self):
        self.post.mark_all_read(self.user)
        self.assertEqual(self.user_feed.read_posts.count(), self.feed.posts.count())

    def test_mark_all_unread(self):
        self.post.mark_all_unread(self.user)
        self.assertEqual(self.user_feed.read_posts.count(), 0)

