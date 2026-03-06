from django.urls import path, include
from order.views import SubscriptionViewSet
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(
    r"subscription-orders", SubscriptionViewSet, basename="subscriptions-orders"
)
urlpatterns = [
    path("", include(router.urls)),
]
