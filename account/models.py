from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from account.utils import generate_otp
from common.generic_model import BaseModel
from tidalvape_be import settings


class AddressType(models.TextChoices):
    HOME = "HOME", "Home"
    OFFICE = "OFFICE", "Office"
    OTHER = "OTHER", "Other"


class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    screen_name = models.CharField(max_length=250, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    role = models.ForeignKey(
        Role, on_delete=models.SET_NULL, null=True, blank=True, related_name="users"
    )
    groups = models.ManyToManyField(Group, related_name="custom_user_set")
    user_permissions = models.ManyToManyField(
        Permission, related_name="custom_user_set"
    )

    def __str__(self):
        return self.username


class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6, default=generate_otp)
    is_valid = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.otp}"


class Address(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="addresses",
        db_index=True,
    )
    flat_name = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    landmark = models.CharField(max_length=255, blank=True)
    address_type = models.CharField(
        max_length=20, choices=AddressType.choices, default=AddressType.HOME
    )
    country = models.CharField(
        max_length=255, blank=True, null=True, default='United Kingdom'
    )
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_default"]),
        ]

    def save(self, *args, **kwargs):
        """
        Ensure only one default address per user.
        """
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).exclude(
                pk=self.pk
            ).update(is_default=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email} - {self.flat_name} ({self.address_type})"


class UserLoyalty(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="user_loyalty",
    )
    points = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.email} - {self.points} points"
