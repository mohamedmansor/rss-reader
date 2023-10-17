import factory
from factory.django import DjangoModelFactory

from rss_reader.feed.models import Feed, Post, UserFeed
from rss_reader.users.tests.factories import UserFactory


class FeedFactory(DjangoModelFactory):
    creator = factory.SubFactory(UserFactory)
    title = factory.Faker("word")
    description = factory.Faker("sentence")
    xml_url = factory.Faker("uri")

    class Meta:
        model = Feed


class PostFactory(DjangoModelFactory):
    feed = factory.SubFactory(FeedFactory)
    title = factory.Faker("word")
    description = factory.Faker("sentence")
    link = factory.Faker("uri")

    class Meta:
        model = Post


class UserFeedFactory(DjangoModelFactory):
    feed = factory.SubFactory(FeedFactory)
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = UserFeed

    @factory.post_generation
    def read_posts(self, create, read_posts, **kwargs):
        if not create:
            return
        if read_posts:
            for order in read_posts:
                self.read_posts.add(read_posts)
