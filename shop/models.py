from django.db import models
from decimal import Decimal
from account.models import User
from common.generic_model import BaseModel, ShopifyBaseModel
from product.models import Product
from django.utils import timezone

# Create your models here.
BANNER_SCREEN = (
    ("desktop", "DESKTOP"),
    ("mobile", "MOBILE"),
)


class Banner(BaseModel):
    image = models.ImageField(upload_to="banner/")
    screen = models.CharField(max_length=20, choices=BANNER_SCREEN, default="desktop")
    endpoint = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=False)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f'{self.screen} - {self.endpoint}'


class Collection(ShopifyBaseModel):
    title = models.CharField(max_length=255)
    handle = models.CharField(max_length=255)
    body_html = models.TextField(null=True, blank=True)
    sort_order = models.CharField(max_length=100, null=True, blank=True)
    template_suffix = models.CharField(max_length=255, null=True, blank=True)
    products_count = models.IntegerField(default=0)
    published_scope = models.CharField(max_length=50, null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    products = models.ManyToManyField(Product, blank=True, related_name="collections")

    def __str__(self):
        return self.title


class ReedemCode(BaseModel):
    reedeem_name = models.CharField(max_length=20)
    discount_percentage = models.PositiveIntegerField()


class UserReedem(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reedem_user")
    reedem_code = models.ForeignKey(
        ReedemCode, on_delete=models.CASCADE, related_name="reedem_code"
    )
    is_used = models.BooleanField(default=False)


class Discount(BaseModel):

    DISCOUNT_TYPE = (
        ("PERCENTAGE", "Percentage"),
        ("FIXED", "Fixed Amount"),
    )

    DISCOUNT_CATEGORY = (
        ("COUPON", "Coupon Code"),
        ("SUBSCRIPTION", "Subscription Discount"),
        ("LOYALTY", "Loyalty Reward"),
        ("AUTOMATIC", "Automatic Discount"),
    )

    code = models.CharField(max_length=50, unique=True, null=True, blank=True)
    label = models.CharField(max_length=100)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE)
    discount_category = models.CharField(
        max_length=20, choices=DISCOUNT_CATEGORY, default="COUPON"
    )
    value = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_order_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    max_discount_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    usage_limit = models.IntegerField(null=True, blank=True)
    used_count = models.IntegerField(default=0)
    points_required = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField(null=True, blank=True)
    valid_to = models.DateTimeField(null=True, blank=True)

    def is_valid(self):
        now = timezone.now()
        return (
            self.is_active
            and self.valid_from <= now <= self.valid_to
            and (self.usage_limit is None or self.used_count < self.usage_limit)
        )

    def __str__(self):
        return f"{self.label} ({self.discount_category})"
