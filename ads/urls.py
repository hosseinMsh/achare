from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AdvertisementViewSet, JobRequestViewSet

router = DefaultRouter()
router.register(r'ads', AdvertisementViewSet, basename='ads')
router.register(r'job-requests', JobRequestViewSet, basename='job-requests')

urlpatterns = [
    path('', include(router.urls)),
]
