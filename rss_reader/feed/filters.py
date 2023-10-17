from django_filters import rest_framework as filters

from rss_reader.feed.models import Post


class PostFilter(filters.FilterSet):
    read = filters.BooleanFilter(method="_filter_read")

    class Meta:
        model = Post
        fields = ["feed", "read"]

    def _filter_read(self, queryset, name, value):
        """
        Filter the given queryset based on the read status of posts.

        :param queryset: The queryset to be filtered.
        :param name: The name of the filter.
        :param value: The value of the filter.

        :return: The filtered queryset.
        """
        if value is None:
            return queryset
        if value is False:
            return queryset.exclude(read_posts__read_posts__in=queryset)
        if value is True:
            return queryset.filter(read_posts__read_posts__in=queryset)
        return queryset
