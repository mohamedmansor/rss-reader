from rest_framework.routers import SimpleRouter

from rrs_reader.feed.api.views import FeedViewSet, PostViewSet

app_name = "feeds"

router = SimpleRouter()
router.register('posts', PostViewSet, basename='posts')
router.register('(?P<feed_id>\d+)/posts', PostViewSet, basename='feed_posts')
router.register('', FeedViewSet, basename='feeds')

urlpatterns = [] + router.urls