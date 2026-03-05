
from django.urls import path, include
from cart.views import CartOverViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
urlpatterns = [
    path("", include(router.urls)),
    path("cart-overview/", CartOverViewSet.as_view(), name="cart-overview")
]