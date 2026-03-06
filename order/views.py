from common.response import StandardPageNumberPagination
from order.filters import SubscriptionFilter
from order.models import Subscription
from order.serializers import SubscriptionSerializer
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions
from django.core.paginator import Paginator, EmptyPage


# Create your views here.
class SubscriptionViewSet(ModelViewSet):
    queryset = Subscription.objects.all().filter(is_delete=False)
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = SubscriptionFilter
    http_method_names = ['get']
    pagination_class = StandardPageNumberPagination
    search_fields = [
        'product__title',
        'product__vendor__name',
        'product__product_type__name',
    ]
    ordering_fields = ['created_at', 'product__title']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset().filter(user=user)
        tab = self.request.query_params.get("tab")
        if tab is not None:
            queryset = queryset.filter(is_active=(tab.lower() == "true"))
        return queryset
