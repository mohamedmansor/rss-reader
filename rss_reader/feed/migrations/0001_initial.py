# Generated by Django 4.2.6 on 2023-10-13 20:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Feed",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now, editable=False, verbose_name="created"
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now, editable=False, verbose_name="modified"
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField()),
                ("xml_url", models.URLField()),
                ("auto_refresh", models.BooleanField(default=True)),
                ("last_refresh_at", models.DateTimeField(auto_now_add=True)),
                (
                    "creator",
                    models.ForeignKey(
                        help_text="Feed creator",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="owner_feeds",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Feed",
                "verbose_name_plural": "Feeds",
                "db_table": "feed",
            },
        ),
        migrations.CreateModel(
            name="UserFeed",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now, editable=False, verbose_name="created"
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now, editable=False, verbose_name="modified"
                    ),
                ),
                ("followed", models.BooleanField(default=False)),
                (
                    "feed",
                    models.ForeignKey(
                        help_text="The feed that is followed/un-followed by users",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="followers",
                        to="feed.feed",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        help_text="The user who follows/un-follows the feed",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="user_feeds",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Post",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now, editable=False, verbose_name="created"
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now, editable=False, verbose_name="modified"
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField()),
                (
                    "status",
                    models.CharField(
                        choices=[("UNREAD", "Unread"), ("READ", "Read")], default="UNREAD", max_length=10
                    ),
                ),
                ("link", models.URLField()),
                ("published_time", models.DateTimeField(blank=True, null=True)),
                ("last_update", models.DateTimeField(blank=True, null=True)),
                (
                    "feed",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="posts", to="feed.feed"
                    ),
                ),
            ],
            options={
                "verbose_name": "Post",
                "verbose_name_plural": "Posts",
                "db_table": "post",
                "ordering": ("-published_time", "-last_update"),
            },
        ),
    ]