from product.models import Product, ProductDeal, ProductImage, ProductOption, ProductTag, ProductVariant
from rest_framework import serializers

class ProductTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductTag
        fields = '__all__'

class ProductVariantSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    class Meta:
        model = ProductVariant
        fields = '__all__'
    
    def get_image(self, obj):
        try:
            image = ProductImage.objects.get(id=obj.image_id)
            return image.image.url if image.image else None
        except ProductImage.DoesNotExist:
            return None
    
class ProductOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductOption
        fields = '__all__'

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = '__all__'
        
class GetProductCardSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    discount_price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'title', 'handle', 'status', 'image', 'price', 'discount_price']

    def get_image(self, obj):
        product_image = obj.images.filter(position=1).first()
        if product_image and product_image.image:
            return product_image.image.url
        return None

    def get_price(self, obj):
        variant = obj.variants.filter(position=1).first()
        if variant:
            return variant.price
        return None

    def get_discount_price(self, obj):
        variant = obj.variants.filter(position=1).first()
        if not variant or not variant.price:
            return None

        original_price = float(variant.price)
        discount_price = original_price - (original_price * 10 / 100)
        return round(discount_price, 2)


class GetProductDetailSerializer(serializers.ModelSerializer):
    vendor = serializers.CharField(source="vendor.name", read_only=True)
    product_type = serializers.CharField(source="product_type.name", read_only=True)
    tags = ProductTagSerializer(read_only=True, many=True)
    variants = ProductVariantSerializer(read_only=True, many=True)
    options = ProductOptionSerializer(read_only=True, many=True)
    images = ProductImageSerializer(read_only=True, many=True)
    
    class Meta:
        model = Product
        fields = ['id', 'title', 'body_html', 'vendor', 'product_type', 'handle', 'status', 'published_scope', 'tags', 'published_at', 'template_suffix', 'variants', 'options', 'images']


class ProductSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = [
            'id',
            'title',
            'body_html',
            'vendor',
            'product_type',
            'handle',
            'status',
            'published_scope',
            'tags',
            'published_at',
            'template_suffix',
            'options'
        ]
        
    def get_options(self, obj):
        return ProductOption.objects.filter(product=obj).first().name


class ProductDealSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductDeal
        fields = [
            "id",
            # "product",
            "deal_name",
            "deal_quantity",
            "deal_price"
        ]