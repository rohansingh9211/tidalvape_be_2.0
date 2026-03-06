from django.db import models

from account.models import User
from common.generic_model import BaseModel
import uuid


# Create your models here.
class Transaction(BaseModel):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
        ("CANCELLED", "Cancelled"),
    ]

    user = models.ForeignKey(
        User, related_name="transactions", on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount_percentage = models.PositiveIntegerField()
    transaction_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    transaction_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDING")
    cyber_transactionid = models.CharField(max_length=150, null=True)
    cyber_status = models.CharField(max_length=50, null=True)

    def __str__(self):
        return f"Transaction {self.id}"
