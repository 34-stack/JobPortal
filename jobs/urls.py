from rest_framework.routers import DefaultRouter
from .views import JobViewSet

# Bug fix: removed duplicate static() — media files are already served
# in the root jobportal/urls.py so it was being registered twice.
router = DefaultRouter()
router.register('', JobViewSet, basename='job')

urlpatterns = router.urls
