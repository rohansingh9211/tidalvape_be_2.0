from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static

from account.views import AuthViewSet, UserAddressViewSet, UserProfileViewSet, UserViewSet

router = DefaultRouter()
router.register(r"auth", AuthViewSet, basename="auth")
router.register(r"userprofiles", UserProfileViewSet)
router.register(r"password", UserViewSet, basename="password")
router.register(r"address", UserAddressViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
