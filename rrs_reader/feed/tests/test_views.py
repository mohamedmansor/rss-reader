from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rrs_reader.feed.models import Feed, Post, UserFeed
from rrs_reader.feed.tests.factories import UserFactory, FeedFactory, PostFactory, UserFeedFactory
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class TestFeedViewSet(APITestCase):
    def setUp(self):
        # Create a test user and authenticate
        self.user = UserFactory()
        self.client.force_authenticate(self.user)

        # Create a test feed
        self.feed = FeedFactory(creator=self.user)

    def test_list_feeds(self):
        url = reverse("feeds:feed-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_feed(self):
        url = reverse("feeds:feed-detail", args=[self.feed.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_feed(self):
        url = reverse("feeds:feed-list")
        new_feed_data = {
            "creator": self.user.pk,
            "xml_url": "https://example.com/new-feed.xml",
        }
        response = self.client.post(url, new_feed_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_feed(self):
        url = reverse("feeds:feed-detail", args=[self.feed.pk])
        updated_data = {"title": "Updated Feed", "description": "Updated Description"}
        response = self.client.patch(url, updated_data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_feed(self):
        url = reverse("feeds:feed-detail", args=[self.feed.pk])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_follow_feed(self):
        url = reverse("feeds:feed-follow", args=[self.feed.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unfollow_feed(self):
        self.feed.follow(self.user)
        url = reverse("feeds:feed-unfollow", args=[self.feed.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unfollow_not_followed_feed_raises_error(self):
        url = reverse("feeds:feed-unfollow", args=[self.feed.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["non_field_errors"], "You're not following this feed.")

    def test_force_update_feed(self):
        url = reverse("feeds:feed-force-update", args=[self.feed.pk])
        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_feed_posts(self):
        url = reverse("feeds:feed-posts", args=[self.feed.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestPostViewSet(APITestCase):
    def setUp(self):
        self.user = UserFactory(username="testuser", password="testpassword")
        self.client.force_authenticate(user=self.user)
        self.feed = FeedFactory.create(creator=self.user)
        self.feed.follow(self.user)
        self.post = PostFactory.create(title="Test Post", description="Test Content", feed=self.feed)

    def test_mark_as_read(self):
        url = reverse("feeds:posts-mark-as-read", args=[self.post.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_feed = UserFeed.objects.filter(user=self.user, feed=self.feed, read_posts__in=[self.post])
        self.assertTrue(user_feed.exists())

    def test_mark_read_posts_as_read(self):
        self.post.mark_as_read(self.user)
        url = reverse("feeds:posts-mark-as-read", args=[self.post.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["non_field_errors"], "You've already marked this feed post as read.")

    def test_mark_as_unread(self):
        self.post.mark_as_read(self.user)
        url = reverse("feeds:posts-mark-as-unread", args=[self.post.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(self.post.read_posts.filter(pk=self.post.pk).exists())

    def test_mark_unread_posts_as_unread(self):
        self.post.mark_as_read(self.user)
        self.post.mark_as_unread(self.user)
        url = reverse("feeds:posts-mark-as-unread", args=[self.post.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["non_field_errors"], "You've already marked this feed post as unread.")
