# views.py
from common.response import StandardAPIResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CartOverviewSerializer
from .services.cart_service import CartService
from rest_framework.permissions import AllowAny

class CartOverViewSet(APIView):
    permission_classes = (AllowAny,)
    def post(self, request):

        serializer = CartOverviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart_items = serializer.validated_data["cart"]
        subscription = serializer.validated_data.get("subscription", True)
        loyalty_discount = serializer.validated_data.get("loyalty_discount", None)
        

        result = CartService.calculate(cart_items, subscription, loyalty_discount)

        return StandardAPIResponse( 
            result,
            status=status.HTTP_200_OK
        )