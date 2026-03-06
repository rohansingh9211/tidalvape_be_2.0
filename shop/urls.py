from django.urls import path, include
from rest_framework.routers import DefaultRouter
from shop.views import (
    BannerViewset,
    GetCollectionListViewSet,
    GetProductsByCollectionViewSet,
    LoyaltyDiscountAvailable,
)

router = DefaultRouter()
router.register(r"banner", BannerViewset, basename="banner-list")
router.register(
    r"collection-list", GetCollectionListViewSet, basename="collection-list"
)
router.register(
    r"collection", GetProductsByCollectionViewSet, basename='products-by-collection'
)

urlpatterns = [
    path("", include(router.urls)),
    path(
        'loyalty-discount/available',
        LoyaltyDiscountAvailable.as_view(),
        name='loyality-discount-available',
    ),
]
