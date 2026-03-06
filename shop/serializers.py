from product.serializers import GetProductCardSerializer
from rest_framework import serializers
from .models import Banner, Collection, Discount


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ['id', 'image', 'screen', 'endpoint']


class GetCollectionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title', 'handle']


class GetProductsByCollectionListSerializer(serializers.ModelSerializer):
    products = GetProductCardSerializer(read_only=True, many=True)

    class Meta:
        model = Collection
        fields = ['id', 'title', 'handle', 'products_count', 'products']


class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = '__all__'
