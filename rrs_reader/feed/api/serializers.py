from rest_framework import serializers

from rrs_reader.feed.models import Feed, Post


class FeedOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feed
        fields = ("id", "creator", "title", "xml_url", "description", "auto_refresh", "last_refresh_at")


class FeedInputSerializer(serializers.ModelSerializer):
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    xml_url = serializers.URLField(required=True)

    class Meta:
        model = Feed
        fields = ("creator", "xml_url")


class PostInputSerializer(serializers.ModelSerializer):
    mark_as_read = serializers.BooleanField(default=False)

    class Meta:
        model = Post
        fields = ("id", "mark_as_read")


class PostOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("id", "feed_id", "title", "description", "link", "published_time", "last_update")
