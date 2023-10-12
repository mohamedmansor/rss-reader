import factory
from factory.django import DjangoModelFactory

from rrs_reader.feed.models import Feed, Post
from rrs_reader.users.tests.factories import UserFactory


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
