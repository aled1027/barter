from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    AccountAPIView,
    UserAPIView,
)

router = DefaultRouter()

urlpatterns = [
    path("", AccountAPIView.as_view(), name="accounts"),
    path("profile/", UserAPIView.as_view(), name="profile"),
]

urlpatterns += router.urls  # type: ignore
