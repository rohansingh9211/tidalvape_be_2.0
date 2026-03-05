from common.response import StandardAPIResponse, StandardPageNumberPagination
from product.serializers import GetProductCardSerializer
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet
from shop.models import Banner, Collection, Discount
from rest_framework import status
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from django.core.paginator import Paginator, EmptyPage
from shop.serializers import BannerSerializer, DiscountSerializer, GetCollectionListSerializer, GetProductsByCollectionListSerializer

class BannerViewset(ModelViewSet):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
    permission_classes = (AllowAny,)
    http_method_names = ['get']

    def list(self, request, *args, **kwargs):
        screen = request.query_params.get('screen')
        queryset = self.get_queryset()
        queryset = queryset.filter(is_active=True, screen=screen)
        serializer = self.get_serializer(queryset, many=True)
        return StandardAPIResponse(serializer.data, status=status.HTTP_200_OK)

class GetCollectionListViewSet(ModelViewSet):
    queryset = Collection.objects.all()
    serializer_class = GetCollectionListSerializer
    permission_classes = (AllowAny,)
    http_method_names = ['get']

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return StandardAPIResponse(serializer.data, status=status.HTTP_200_OK)


class GetProductsByCollectionViewSet(ModelViewSet):
    queryset = Collection.objects.all()
    serializer_class = GetProductsByCollectionListSerializer
    permission_classes = (AllowAny,)
    http_method_names = ['get']
    lookup_field = "handle"
    
    def list(self, request, *args, **kwargs):
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 10))
        collections = self.get_queryset()
        response_data = []
        for collection in collections:
            products = collection.products.all()
            paginator = Paginator(products, page_size)
            try:
                paginated_products = paginator.page(page)
            except EmptyPage:
                paginated_products = []
            serialized_products = GetProductCardSerializer(
                paginated_products,
                many=True,
                context={"request": request}
            ).data
            response_data.append({
                "id": collection.id,
                "title": collection.title,
                "handle": collection.handle,
                "products_count": products.count(),
                "total_pages": paginator.num_pages,
                "current_page": page,
                "products": serialized_products
            })
        return StandardAPIResponse(response_data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'], url_path='products')
    def products(self, request, handle=None):
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 10))
        collection = get_object_or_404(Collection, handle=handle)
        products = collection.products.all()
        paginator = Paginator(products, page_size)
        try:
            paginated_products = paginator.page(page)
        except EmptyPage:
            paginated_products = []

        serializer = GetProductCardSerializer(
            paginated_products,
            many=True,
            context={"request": request}
        )

        response_data = {
            "id": collection.id,
            "title": collection.title,
            "handle": collection.handle,
            "body_html": collection.body_html,
            "sort_order": collection.sort_order,
            "template_suffix": collection.template_suffix,
            "published_scope": collection.published_scope,
            "products_count": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": page,
            "products": serializer.data
        }

        return StandardAPIResponse(response_data, status=status.HTTP_200_OK)
    
class LoyaltyDiscountAvailable(APIView):
    permission_classes = (AllowAny,)
    
    def get(self, request, *args, **kwargs):
        loyalty_coin = request.query_params.get("loyalty_coin")
        loyalty_discount = Discount.objects.filter(
            discount_category='LOYALTY',
            used_count__lte = loyalty_coin,
            points_required__lte = loyalty_coin,
            is_active = True
        )
        serializer = DiscountSerializer(loyalty_discount, many=True)
        return StandardAPIResponse(
            serializer.data,
            status=status.HTTP_200_OK
        )