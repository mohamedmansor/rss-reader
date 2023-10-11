from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils import Choices
from model_utils.models import TimeStampedModel


class Feed(TimeStampedModel):
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owner_feeds", help_text="Feed creator"
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    # publisher_mail = models.EmailField(max_length=254)
    xml_url = models.URLField()
    auto_refresh = models.BooleanField(default=True)
    last_refresh_at = models.DateTimeField(auto_now_add=True)

    def deactivate_auto_refresh(self):
        self.auto_refresh = False
        self.save(update_fields=["auto_refresh"])

    class Meta:
        db_table = "feed"
        verbose_name = "Feed"
        verbose_name_plural = "Feeds"

    def __str__(self):
        return f"{self.pk}: {self.title}"


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
    followed = models.BooleanField(default=False)


class Post(TimeStampedModel):
    STATUSES = Choices(
        ("UNREAD", _("Unread")),
        ("READ", _("Read")),
    )
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE, related_name="posts")
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(choices=STATUSES, default=STATUSES.UNREAD, max_length=10)
    link = models.URLField()
    published_time = models.DateTimeField(null=True, blank=True)
    last_update = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "post"
        verbose_name = "Post"
        verbose_name_plural = "Posts"
        ordering = ("-published_time", "-last_update")

    def __str__(self):
        return f"{self.pk}: {self.title}"
