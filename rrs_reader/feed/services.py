import logging

import feedparser
from dateutil import parser
from django.core.mail import send_mail
from rrs_reader.feed.exceptions import FeedException
from django.utils import timezone

from rrs_reader.feed.models import Feed, Post

logger = logging.getLogger(__name__)


class FeedService:
    """
    Feed Service that parse feed and posts

    Usage:
        - Initate FeedService object with feed model instance
            `feed_svc = FeedService(feed)`
        - Update feed and post
            `feed_svc.update_feed()`
        - Get raw parsed data
            `feed_svc.parse_rrs_link()`
    """

    def __init__(self, feed: Feed):
        self.feed = feed

    def parse_rrs_link(self):
        """
        Parse RRS link Using feedparser

        - Returns:
            parsed (dict): Parsed object for this RSS link
        """
        link = self.feed.xml_url
        parsed_data = feedparser.parse(link)
        if parsed_data.get("bozo_exception"):
            msg = 'Found Malformed feed, "%s": %s' % (parsed_data.get("href"), parsed_data.get("bozo_exception"))
            logger.warning(msg)
            raise FeedException(details=msg)
        return parsed_data

    def _prepare_feed_fields(self, feed_dict):
        if not ["link", "title", "subtitle"] in feed_dict.keys():
            raise FeedException(details="Feed attributes are not valid")

        fields = {
            "title": feed_dict.get("title"),
            "link": feed_dict.get("link"),
            "description": feed_dict.get("subtitle"),
        }
        return fields

    def _prepare_post_fields(self, post_entity):
        """
        Prepare post fields based scraped post attrs.

        Parameters:
            post_entity (dict): Object from feedparser.FeedParserDict

        Returns:
            fields (dict): All needed fields to create an post object

        """
        if not ["link", "title", "summary", "published"] in post_entity.keys():
            raise FeedException(details="Post attributes are not valid")

        fields = {
            "title": post_entity.get("title"),
            "description": post_entity.get("summary"),
            "link": post_entity.get("link"),
            "published_time": parser.parse(post_entity.get("published")),
        }
        return fields

    def update_feed(self):
        """
        Update the feed object and it's posts based on the scraped data.
        Will create new post if it does not exist or update the existing ones.


        Returns:
            count (int): new created posts count.

        """
        parsed_data = self.parse_rrs_link()
        feed_dict = parsed_data.get("feed", {})
        post_entries = parsed_data.get("entries", {})

        feed_fields = self._prepare_feed_fields(feed_dict)
        for field, value in feed_fields.items():
            setattr(self.feed, field, value)
        self.feed.last_update = timezone.now()
        self.feed.save()

        total_created_posts = 0
        for post in post_entries:
            fields = self._prepare_post_fields(post)
            fields["last_update"] = timezone.now()
            _, created = Post.objects.update_or_create(link=fields.pop("link"), feed=self.feed, defaults=fields)
            if created:
                total_created_posts += 1
        return total_created_posts


class NotificationService:
    @staticmethod
    def notify(user, subject, message):
        """
        Send email notification to the user

        Parameters:
            user (obj): User object
            subject (str): subject text
            message (str): message text

        Returns:
            (bool): Success or Failure
        """
        return send_mail(subject, message, "noreply@rrsreader.com", [user.email], fail_silently=False)
