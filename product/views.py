from common.exception import StandardAPIException
from common.response import StandardAPIResponse, StandardPageNumberPagination
from product.models import Product
from product.serializers import GetProductCardSerializer, GetProductDetailSerializer
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter

class GetProdcutCardListViewSet(ModelViewSet):
    queryset = Product.objects.prefetch_related("images", "variants")
    serializer_class = GetProductCardSerializer
    permission_classes = (AllowAny,)
    http_method_names = ['get']
    pagination_class = StandardPageNumberPagination
    filter_backends = [SearchFilter, OrderingFilter]
    lookup_field = "handle"
    search_fields = [
        'title',
        'vendor__name',
        'product_type__name',
        'tags__name',
        'variants__sku'
    ]
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']

    @action(detail=True, methods=['get'], url_path='similar')
    def similar_products(self, request, handle=None):
        product = get_object_or_404(Product, handle=handle)
        similar_products = Product.objects.filter(
            product_type=product.product_type
        ).exclude(
            id=product.id
        ).annotate(
            same_tags=Count(
                'tags',
                filter=Q(tags__in=product.tags.all())
            )
        ).order_by(
            '-same_tags',
            '-created_at'
        )
        page = self.paginate_queryset(similar_products)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(similar_products, many=True)
        return StandardAPIResponse(serializer.data)


class GetProductDetailViewSet(ModelViewSet):
    queryset = Product.objects.select_related(
        "vendor", "product_type"
    ).prefetch_related(
        "images", "variants", "options", "tags"
    )
    serializer_class = GetProductDetailSerializer
    permission_classes = (AllowAny,)
    http_method_names = ['get']
    lookup_field = "handle"
    pagination_class = StandardPageNumberPagination