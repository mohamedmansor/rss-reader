from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from rss_reader.feed.api.serializers import (
    FeedInputSerializer,
    FeedOutputSerializer,
    PostInputSerializer,
    PostOutputSerializer,
)
from rss_reader.feed.filters import PostFilter
from rss_reader.feed.models import Feed, Post
from rss_reader.feed.tasks import refresh_feed


class FeedViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    queryset = Feed.objects.all()

    def get_serializer_class(self):
        """
        Get the serializer class based on the action.

        Returns:
            FeedInputSerializer: If the action is "create".
            FeedOutputSerializer: Otherwise.
        """
        if self.action == "create":
            return FeedInputSerializer
        return FeedOutputSerializer

    def get_queryset(self):
        """
        Returns a queryset of Feed objects filtered by the creator being the current user.
        """
        return self.queryset.filter(creator=self.request.user)

    def perform_create(self, serializer):
        instance = serializer.save()
        refresh_feed.delay(instance.id)
        return Response(
            {"details": _("Feed created, the post feed will be updated shortly")}, status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=["POST"])
    def follow(self, request, *args, **kwargs):
        """
        Enables authenticated users to follows a specific feed using feed pk(int)

        :param kwargs:
            - pk (int) which used to get the feed instance from DB.

        Returns:
            Response: The HTTP response object containing the serialized data of the updated instance.
            - `200 OK` if a UserFeed object is created.
            - `400 Bad Request` if the feed is already followed.
            - `403 Forbidden` if the user is anonymous.
        """

        instance = self.get_object()

        instance.follow(self.request.user)
        return Response(self.get_serializer(instance).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["POST"])
    def unfollow(self, request, *args, **kwargs):
        """
        Enables authenticated users to stop following a followed feed instance.

        :param kwargs:
            - pk (int) which used to get the feed instance from DB.

        :return:
            - `200 OK` if the feed instance is_followed value changed to False.
            - `400 Bad Request` if the feed instance is already unfollowed.
            - `403 Forbidden` if the user is anonymous.
        """
        instance = self.get_object()

        instance.unfollow(self.request.user)
        return Response(self.get_serializer(instance).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["PUT"], url_path="force-update")
    def force_update(self, request, *args, **kwargs):
        """
        Enables authenticated users to force update a feed instance.
        Also, if the automatic update is not active for the feed it'll be activated.

        :param kwargs:
            - pk (int) which used to get the feed instance from DB.

        :return:
            - `200 OK` after running a background task to force update a feed instance.
            - `403 Forbidden` if the user is anonymous.
            - `404 Not Found` if provided feed doesn't exist or not created by the authenticated user.
        """
        instance = self.get_object()

        if not instance.auto_refresh:
            instance.activate_auto_refresh()

        refresh_feed.delay(instance.id)
        return Response(self.get_serializer(instance).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["GET"], url_path="posts")
    def posts(self, request, *args, **kwargs):
        """
        Enables authenticated users to retrieve a paginated list of posts related to the passed feed ID.
        Also, if the automatic update is not active for the feed it'll be activated.

        :param kwargs:
            - pk (int) which used to get the feed instance from DB, and then its related posts.

        :return:
            - `200 OK`
            - `403 Forbidden` if the user is anonymous.
        """
        instance = self.get_object()
        posts_queryset = instance.posts.all()
        serializer = PostOutputSerializer(posts_queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PostViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = Post.objects.select_related("feed").prefetch_related("read_posts").all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = PostFilter

    def get_serializer_class(self):
        """
        Get the serializer class based on the action.
        """
        if self.action == "retrieve":
            return PostOutputSerializer
        return PostInputSerializer

    def get_queryset(self):
        """
        :return: all the feeds posts registered by the authenticated user.
        """
        return self.queryset.filter(feed__creator=self.request.user)

    @action(detail=True, methods=["POST"], url_path="mark-as-read")
    def mark_as_read(self, request, *args, **kwargs):
        """
        Enables authenticated users to change feed post status to be read.

        :param kwargs:
            - pk (int) which used to get the feed post instance from DB.

        :return:
            - `200 OK` if the feed post instance status is new and changed to read.
            - `400 Bad Request` if the feed post instance status is already read.
            - `403 Forbidden` if the user is anonymous.
        """
        instance = self.get_object()
        instance.mark_as_read(self.request.user)
        return Response(self.get_serializer(instance).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["POST"], url_path="mark-as-unread")
    def mark_as_unread(self, request, *args, **kwargs):
        """
        Enables authenticated users to change feed post status to be read.

        :param kwargs:
            - pk (int) which used to get the feed post instance from DB.

        :return:
            - `200 OK` if the feed post instance status is new and changed to unread.
            - `400 Bad Request` if the feed post instance status is already unread.
            - `403 Forbidden` if the user is anonymous.
        """
        instance = self.get_object()
        instance.mark_as_unread(self.request.user)
        return Response(self.get_serializer(instance).data, status=status.HTTP_200_OK)
