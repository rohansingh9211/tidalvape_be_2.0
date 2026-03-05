# serializers.py
from rest_framework import serializers


class CartItemSerializer(serializers.Serializer):
    product = serializers.IntegerField(required=False)
    variant = serializers.IntegerField(required=False)
    quantity = serializers.IntegerField(min_value=1, default=1)


class CartOverviewSerializer(serializers.Serializer):
    cart = CartItemSerializer(many=True)
    subscription = serializers.BooleanField(
        required=False,
        default=False
    ) # Only one subscription discount in Discount table
    loyalty_discount = serializers.IntegerField(
        required=False,
        allow_null=True
    )