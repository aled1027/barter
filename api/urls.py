from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

router.register(r"instruments", views.InstrumentViewSet)
router.register(r"instruments", views.InstrumentViewSet)

urlpatterns = [
    path("check/", views.investment_check, name="create"),
]

urlpatterns += router.urls  # type: ignore
