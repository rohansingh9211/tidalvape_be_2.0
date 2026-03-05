from django_filters import rest_framework as filters

from order.models import Subscription

class SubscriptionFilter(filters.FilterSet):
    user_id = filters.NumberFilter(field_name='user__id')

    class Meta:
        model = Subscription
        fields = ['product__title']