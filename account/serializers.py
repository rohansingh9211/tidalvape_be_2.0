from account.models import Address, User, UserLoyalty
from rest_framework import serializers
from django.contrib.auth import authenticate


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "password")
        # extra_kwargs = {"password": {"write_only": True}}

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User already exists.")
        return value

    def create(self, validated_data):
        password = (
            validated_data["password"]
            if "password" in validated_data
            else validated_data["email"]
        )
        user = User.objects.create_user(
            username=validated_data["email"],
            password=password,
            email=validated_data["email"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        if email and password:
            user = authenticate(username=email, password=password)
            print(user, '---------ehllo usrr')
            if user:
                if not user.is_active:
                    raise serializers.ValidationError("User is inactive.")
                return user
            else:
                return {"error": "Invalid credentials"}
                #  raise serializers.ValidationError("Invalid credentials")
        else:
            raise serializers.ValidationError("Must include 'email' and 'password'")


class UserProfileSerializer(serializers.ModelSerializer):
    loyalty_point = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "screen_name",
            "date_of_birth",
            "gender",
            "phone_number",
            "loyalty_point",
        ]

    def get_loyalty_point(self, obj):
        return UserLoyalty.objects.get(user=obj).points


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)
    otp = serializers.CharField(write_only=True, required=False, allow_blank=True)
    new_password = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )

    def validate(self, data):
        otp = data.get("otp")
        new_password = data.get("new_password")

        if new_password and not otp:
            raise serializers.ValidationError(
                "OTP must be provided if new password is given."
            )

        return data


class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            "id",
            "flat_name",
            "city",
            "zip_code",
            "flat_name",
            # "street",
            "landmark",
            "address_type",
            "is_default",
        ]
        read_only_fields = ["user"]

    def create(self, validated_data):
        request = self.context.get("request", None)
        if request and request.user.is_authenticated:
            validated_data["user"] = request.user
        return super().create(validated_data)
