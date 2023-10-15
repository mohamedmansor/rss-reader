from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from rrs_reader.feed.models import Feed, Post


class PostAdminInline(admin.StackedInline):
    model = Post
    fields = ("created", "title", "description", "link", "published_time", "last_update")
    readonly_fields = ["created", "last_update"]
    classes = ["collapse"]

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj):
        return False


@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {"fields": ("creator", "title", "description", "xml_url", "auto_refresh")}),
        (_("Important dates"), {"fields": ("last_refresh_at", "created", "modified")}),
    )
    list_display = ["creator", "title", "auto_refresh"]
    readonly_fields = ["creator", "last_refresh_at", "created", "modified"]
    search_fields = ["title"]
    list_filter = ["auto_refresh"]
    inlines = [PostAdminInline]
