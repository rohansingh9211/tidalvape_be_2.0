from account.serializers import UserProfileSerializer
from order.models import Order, OrderItems, Subscription
from product.serializers import GetProductDetailSerializer, ProductDealSerializer, ProductSerializer, ProductVariantSerializer
from rest_framework import serializers


class OrderItemSerializer(serializers.ModelSerializer):
    product = GetProductDetailSerializer()
    product_varient = ProductVariantSerializer(read_only=True)
    class Meta:
        model = OrderItems
        fields = [
            'id', 
            'order', 
            'product', 
            'quantity', 
            'product_varient', 
            'price', 
            # 'is_subscribed', 
            'total_price',
            'created_at', 
            'updated_at',
            'is_delete'
        ]
    
class UserOrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    user = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'order_id', 'user', 'transaction', 'delivery_charge', 'total_price', 'sub_total_price', 'discount_amount', 'status', 'address', 'order_status', 'order_items', 'tracking_id', 'is_subscribed', 'created_at', 'updated_at', 'is_delete']
        

class SubscriptionSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer()
    product = ProductSerializer(read_only=True)
    product_varient = ProductVariantSerializer(read_only=True)

    class Meta:
        model = Subscription
        fields = [
            "id",
            "user",
            "product",
            "product_varient",
            "order",
            "days",
            "is_active",
            'address',
            "quantity",
            "discount_amount",
            "delivery_charge",
            "price",
            "sub_total",
            "total_price",
            "is_delete",
            "created_at",
            "updated_at"
        ]