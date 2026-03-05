from django.urls import path, include
from product.views import GetProdcutCardListViewSet, GetProductDetailViewSet
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r"product-card-list", GetProdcutCardListViewSet, basename="product-card-list")
router.register(r"product", GetProductDetailViewSet, basename="product-detail")

urlpatterns = [
    path("", include(router.urls)),
    
]
