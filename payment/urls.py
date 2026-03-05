from django.urls import path, include
from payment.views import CspEnrollWebPendingAuthenticationView
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
urlpatterns = [
    path("", include(router.urls)),
    path('csp/payment', CspEnrollWebPendingAuthenticationView.as_view(), name='enrollwebauth'),
    
]
