from django_filters import rest_framework as filters

from order.models import Subscription


class SubscriptionFilter(filters.FilterSet):
    user_id = filters.NumberFilter(field_name='user__id')
    start_date = filters.DateTimeFilter(
        field_name="created_at",
        lookup_expr="gte"
    )

    end_date = filters.DateTimeFilter(
        field_name="created_at",
        lookup_expr="lte"
    )
    
    payment_status = filters.CharFilter(
        field_name="order__status"
    )

    order_status = filters.CharFilter(
        field_name="order__order_status"
    )
    class Meta:
        model = Subscription
        fields = [
            "user_id",
            "product__title",
            "start_date",
            "end_date",
            "payment_status",
            "order_status",
        ]
