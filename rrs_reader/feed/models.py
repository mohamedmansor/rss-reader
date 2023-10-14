from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel
from django.core.validators import ValidationError


class Feed(TimeStampedModel):
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owner_feeds", help_text="Feed creator"
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    xml_url = models.URLField()
    auto_refresh = models.BooleanField(default=True)
    last_refresh_at = models.DateTimeField(auto_now_add=True)

    def deactivate_auto_refresh(self):
        self.auto_refresh = False
        self.save(update_fields=["auto_refresh"])

    def activate_auto_refresh(self):
        self.auto_refresh = True
        self.save(update_fields=["auto_refresh"])

    def is_followed_by_user(self, user):
        return UserFeed.objects.filter(user=user, feed=self).exists()

    def follow(self, user):
        obj, created = UserFeed.objects.get_or_create(user=user, feed=self)
        if not created:
            raise ValidationError(_("You've already followed this feed."))
        return obj

    def unfollow(self, user):
        UserFeed.objects.filter(user=user, feed=self).delete()

    class Meta:
        db_table = "feed"
        verbose_name = "Feed"
        verbose_name_plural = "Feeds"

    def __str__(self):
        return f"{self.pk}: {self.title}"


class Post(TimeStampedModel):
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE, related_name="posts")
    title = models.CharField(max_length=255)
    description = models.TextField()
    link = models.URLField()
    published_time = models.DateTimeField(null=True, blank=True)
    last_update = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "post"
        verbose_name = "Post"
        verbose_name_plural = "Posts"
        ordering = ["-last_update"]

    def __str__(self):
        return f"{self.pk}: {self.title}"

    def mark_as_read(self, user):
        """
        Marks a feed post as read for a given user.

        Parameters:
            user (User): The user for whom the feed post should be marked as read.

        Raises:
            ValidationError: If the feed post has already been marked as read by the user.

        Returns:
            None
        """
        user_feed = UserFeed.objects.filter(user=user, feed=self.feed).last()
        if self in user_feed.read_posts.all():
            raise ValidationError(_("You've already marked this feed post as read."))

        user_feed.read_posts.add(self)
        user_feed.save()

    def mark_as_unread(self, user):
        """
        Marks a feed post as unread for a given user.

        Parameters:
            user (User): The user for whom the feed post should be marked as unread.

        Raises:
            ValidationError: If the feed post has already been marked as unread.

        Returns:
            None
        """
        user_feed = UserFeed.objects.filter(user=user, feed=self.feed).last()
        if not self in user_feed.read_posts.all():
            raise ValidationError(_("You've already marked this feed post as unread."))
        user_feed.read_posts.remove(self)
        user_feed.save()

    def mark_all_read(self, user):
        """
        Marks all posts in the feed as read for a given user.

        Args:
            user (User): The user for whom the posts will be marked as read.

        Returns:
            None
        """
        user_feed = UserFeed.objects.filter(user=user, feed=self.feed).last()
        user_feed.read_posts.add(*[post for post in self.feed.posts.all()])

    def mark_all_unread(self, user):
        """
        Marks all posts in the user's feed as unread.

        Args:
            user (User): The user for whom to mark the posts as unread.

        Returns:
            None
        """
        user_feed = UserFeed.objects.filter(user=user, feed=self.feed).last()
        user_feed.read_posts.clear()


class UserFeed(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_feeds",
        help_text="The user who follows/un-follows the feed",
    )
    feed = models.ForeignKey(
        Feed,
        on_delete=models.CASCADE,
        related_name="followers",
        help_text="The feed that is followed/un-followed by users",
    )
    read_posts = models.ManyToManyField(
        Post, blank=True, related_name="read_posts", help_text="Posts that read by the user"
    )
