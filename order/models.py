from django.db import models
import uuid
from account.models import User
from common.generic_model import BaseModel
from payment.models import Transaction
from product.models import Product, ProductVariant
from django.core.exceptions import ValidationError

# Create your models here.


class Subscription(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(
        "Order", on_delete=models.CASCADE, related_name="subscribe_order"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_varient = models.ForeignKey(
        ProductVariant, on_delete=models.CASCADE, null=True, blank=True
    )
    days = models.JSONField()
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    quantity = models.IntegerField(default=0)
    discount_amount = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)
    delivery_charge = models.DecimalField(default=5.49, max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    sub_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    address = models.CharField(max_length=350, null=True)

    def __str__(self):
        return f"{self.user.username} - Subscription"


class Order(BaseModel):
    payment_stauts_type = [
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
        ("PENDING", "Pending"),
    ]
    ORDER_STATUS_CHOICES = [
        ("PROCESSING", "Processing"),
        ("SHIPPED", "Shipped"),
        ("DELIVERED", "Delivered"),
        ("CANCELLED", "Cancelled"),
    ]
    order_id = models.CharField(max_length=10, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="order_user")
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    sub_total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    shopify_order_id = models.BigIntegerField(null=True, blank=True)
    shopify_response = models.TextField(null=True, blank=True)
    status = models.CharField(
        max_length=50, choices=payment_stauts_type, default="PENDING"
    )
    order_status = models.CharField(
        max_length=50, choices=ORDER_STATUS_CHOICES, default="PROCESSING"
    )
    address = models.CharField(max_length=350, null=False)
    is_subscribed = models.BooleanField(default=False)
    payload = models.TextField(blank=True)
    tracking_id = models.CharField(max_length=50, blank=True)
    is_delete = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.order_id} - {self.user.username}"


class OrderItems(BaseModel):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="order_items"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_varient = models.ForeignKey(
        ProductVariant, on_delete=models.CASCADE, null=True, blank=True
    )
    quantity = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    # apply_deal = models.ForeignKey(ProductDeal, on_delete=models.SET_NULL, related_name="orderitem_deal", null=True, blank=True)
    is_delete = models.BooleanField(default=False)

    def clean(self):
        if self.order and not self.order.pk:
            raise ValidationError("Order does not exist.")
        if self.product and not self.product.pk:
            raise ValidationError("Product does not exist.")
        if self.product_varient and not self.product_varient.pk:
            raise ValidationError("Product MetaData does not exist.")

    def __str__(self):
        return f"{self.order.id} - {self.product.title}"


class LoyaltyTransaction(models.Model):

    TRANSACTION_TYPE = (
        ("EARN", "Earned"),
        ("REDEEM", "Redeemed"),
        ("EXPIRE", "Expired"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    points = models.IntegerField()
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE)

    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
