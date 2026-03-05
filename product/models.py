from django.db import models
from common.generic_model import BaseModel, ShopifyBaseModel


class Vendor(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class ProductType(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class ProductTag(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Product(ShopifyBaseModel):
    title = models.CharField(max_length=500)
    body_html = models.TextField(null=True, blank=True)
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    product_type = models.ForeignKey(
        ProductType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    handle = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True)
    published_scope = models.CharField(max_length=50, null=True, blank=True)
    tags = models.ManyToManyField(ProductTag, blank=True, related_name="products")
    published_at = models.DateTimeField(null=True, blank=True)
    template_suffix = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.title


class ProductVariant(ShopifyBaseModel):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="variants"
    )
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    position = models.IntegerField(null=True, blank=True)
    inventory_policy = models.CharField(max_length=50, null=True, blank=True)
    compare_at_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    option1 = models.CharField(max_length=255, null=True, blank=True)
    option2 = models.CharField(max_length=255, null=True, blank=True)
    option3 = models.CharField(max_length=255, null=True, blank=True)
    taxable = models.BooleanField(default=True)
    barcode = models.CharField(max_length=255, null=True, blank=True)
    fulfillment_service = models.CharField(max_length=255, null=True, blank=True)
    grams = models.IntegerField(null=True, blank=True)
    inventory_management = models.CharField(max_length=255, null=True, blank=True)
    requires_shipping = models.BooleanField(default=True)
    sku = models.CharField(max_length=255, null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    weight_unit = models.CharField(max_length=50, null=True, blank=True)
    inventory_item_id = models.BigIntegerField(null=True, blank=True)
    inventory_quantity = models.IntegerField(null=True, blank=True)
    image_id = models.BigIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.product.title} - {self.title}"


class ProductOption(ShopifyBaseModel):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="options"
    )

    name = models.CharField(max_length=255)
    position = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.product.title} - {self.name}"


class ProductImage(ShopifyBaseModel):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )

    alt = models.CharField(max_length=255, null=True, blank=True)
    position = models.IntegerField(null=True, blank=True)
    image = models.ImageField(upload_to="products/")
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.product.title} Image"

class ProductDeal(BaseModel):
    DEAL_TYPE_CHOICES = (
        ("fixed", "Fixed Price"),        # Buy X for £Y
        ("percentage", "Percentage"),    # 10% off
    )
    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        related_name="deals",
        db_index=True
    )
    deal_name = models.CharField(max_length=150)
    deal_quantity = models.PositiveIntegerField(default=1)
    deal_type = models.CharField(
        max_length=20,
        choices=DEAL_TYPE_CHOICES,
        default="fixed"
    )
    deal_value = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.product.title} - {self.deal_name}"
    