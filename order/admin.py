from django.contrib import admin

from order.models import Order, OrderItems, Subscription

# Register your models here.
admin.site.register(Order)
admin.site.register(OrderItems)
admin.site.register(Subscription)
