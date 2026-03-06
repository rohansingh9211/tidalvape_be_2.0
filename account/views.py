import json
import requests
from account.models import OTP, Address, User, UserLoyalty
from account.serializers import (
    LoginSerializer,
    RegisterSerializer,
    ResetPasswordSerializer,
    UserAddressSerializer,
    UserProfileSerializer,
)
from account.utils import create_otp
from common.exception import StandardAPIException
from common.response import StandardAPIResponse
from rest_framework import viewsets, permissions
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.hashers import make_password

from data.error import ERROR_DETAILS


# Create your views here.
class AuthViewSet(viewsets.ViewSet):
    permission_classes = (AllowAny,)

    # @swagger_auto_schema(request_body=RegisterSerializer)
    @action(detail=False, methods=["post"], url_path="register")
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return StandardAPIResponse(
            {
                "username": user.username,
                "email": user.email,
                "refresh_token": str(refresh),
                "access_token": str(refresh.access_token),
                "id": user.id,
            },
            status=status.HTTP_201_CREATED,
        )

    # @swagger_auto_schema(request_body=LoginSerializer)
    @action(detail=False, methods=["post"], url_path="login")
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        try:
            refresh = RefreshToken.for_user(user)
            loyalty_obj, created = UserLoyalty.objects.get_or_create(user=user)
            return StandardAPIResponse(
                data={
                    "refresh_token": str(refresh),
                    "access_token": str(refresh.access_token),
                    "id": user.id,
                    "loyalty_point": loyalty_obj.points,
                },
                status=status.HTTP_200_OK,
            )
        except:
            raise StandardAPIException(
                code='error',
                detail=user["error"],
                status_code=status.HTTP_400_BAD_REQUEST,
            )


class UserProfileViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer


class UserViewSet(viewsets.ViewSet):
    # @swagger_auto_schema(request_body=ResetPasswordSerializer)
    @action(detail=False, methods=["post"], url_path="reset-password")
    def reset_password(self, request):
        serializer = ResetPasswordSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            email = serializer.validated_data["email"]
            otp = serializer.validated_data.get("otp", None)
            new_password = serializer.validated_data.get("new_password", None)
            user = User.objects.filter(email=email).first()

            if user:
                if otp is None and new_password is None:
                    otp_instance = OTP.objects.create(user=user)
                    if otp_instance:
                        create_otp(user.email, otp_instance.otp)
                    return StandardAPIResponse(
                        {"message": "OTP sent successfully."}, status=status.HTTP_200_OK
                    )
                elif otp and new_password is None:
                    otp_instance = OTP.objects.filter(
                        user=user, otp=otp, is_valid=True
                    ).first()
                    if (
                        otp_instance
                        and otp_instance.created_at + timedelta(minutes=10)
                        > timezone.now()
                    ):
                        otp_instance.is_valid = True
                        otp_instance.save()
                        return StandardAPIResponse(
                            {"message": "OTP validated successfully."},
                            status=status.HTTP_200_OK,
                        )
                    raise StandardAPIException(
                        code="otp_expired",
                        detail=ERROR_DETAILS["otp_expired"],
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                elif otp and new_password:
                    otp_instance = OTP.objects.filter(
                        user=user, otp=otp, is_valid=True
                    ).first()
                    if (
                        otp_instance
                        and otp_instance.created_at + timedelta(minutes=10)
                        > timezone.now()
                    ):
                        otp_instance.is_valid = False
                        otp_instance.save()
                        user = User.objects.get(id=user.id)
                        user.password = make_password(new_password)
                        user.save()
                        OTP.objects.filter(user=user, otp=otp).delete()
                        return StandardAPIResponse(
                            {"message": "Password updated successfully."},
                            status=status.HTTP_200_OK,
                        )
                    raise StandardAPIException(
                        code="otp_expired",
                        detail=ERROR_DETAILS["otp_expired"],
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                else:
                    return StandardAPIResponse(
                        code="invalid_request",
                        detail=ERROR_DETAILS["invalid_request"],
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                return StandardAPIResponse(
                    code="user_not_found",
                    detail=ERROR_DETAILS["user_not_found"],
                    status=status.HTTP_404_NOT_FOUND,
                )


class UserAddressViewSet(ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = UserAddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Address.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return StandardAPIResponse(serializer.data, status=status.HTTP_200_OK)
