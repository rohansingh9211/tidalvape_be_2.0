from decimal import Decimal, ROUND_DOWN
from django.utils import timezone
from django.shortcuts import get_object_or_404

from product.models import Product, ProductVariant
from shop.models import Discount


class CartService:

    DELIVERY_THRESHOLD = Decimal("24.00")
    DELIVERY_CHARGE = Decimal("5.49")

    @staticmethod
    def calculate(cart_items, subscription=False, loyalty_discount_id=None):

        sub_total = Decimal("0.00")

        # -------------------------
        # Calculate Subtotal
        # -------------------------
        for item in cart_items:
            quantity = Decimal(item["quantity"])

            if item.get("variant"):
                variant = get_object_or_404(ProductVariant, id=item["variant"])
                price = variant.price
            else:
                product = get_object_or_404(Product, id=item["product"])
                price = product.price

            sub_total += price * quantity

        sub_total = CartService._truncate(sub_total)

        now = timezone.now()

        subscription_discount = None
        loyalty_discount = None

        if subscription:
            subscription_discount = Discount.objects.filter(
                discount_category="SUBSCRIPTION", is_active=True
            ).first()

        loyalty_discount = None

        if loyalty_discount_id:
            print(loyalty_discount, '----------loyalty_discount')
            loyalty_discount = Discount.objects.filter(
                id=loyalty_discount_id, discount_category="LOYALTY", is_active=True
            ).first()

        # -------------------------
        # Calculate Discounts
        # -------------------------
        subscription_discount_amt = Decimal("0.00")
        loyalty_discount_amt = Decimal("0.00")

        if subscription_discount:
            subscription_discount_amt = CartService._calculate_discount(
                sub_total, subscription_discount
            )

        if loyalty_discount:
            loyalty_discount_amt = CartService._calculate_discount(
                sub_total, loyalty_discount
            )

        total_discount = subscription_discount_amt + loyalty_discount_amt

        delivery_charge = (
            CartService.DELIVERY_CHARGE
            if sub_total < CartService.DELIVERY_THRESHOLD
            else Decimal("0.00")
        )

        grand_total = sub_total - total_discount + delivery_charge
        grand_total = CartService._truncate(grand_total)

        return {
            "sub_total": CartService._format(sub_total),
            "discount": {
                "subscription": (
                    {
                        "label": (
                            subscription_discount.label
                            if subscription_discount
                            else None
                        ),
                        "discount": (
                            f"£{CartService._format(subscription_discount_amt)} ({int(subscription_discount.value)}{'%' if subscription_discount.discount_type == 'PERCENTAGE' else '£'})"
                            if subscription_discount
                            else None
                        ),
                    }
                    if subscription_discount
                    else None
                ),
                "loyalty": (
                    {
                        "label": loyalty_discount.label if loyalty_discount else None,
                        "discount": (
                            (
                                f"£{CartService._format(subscription_discount_amt)} "
                                f"({int(loyalty_discount.value)}"
                                f"{'%' if loyalty_discount and loyalty_discount.discount_type == 'PERCENTAGE' else '£'})"
                                if subscription_discount
                                else None
                            )
                            if loyalty_discount
                            else None
                        ),
                    }
                    if loyalty_discount
                    else None
                ),
            },
            "delivery_charge": CartService._format(delivery_charge),
            "grand_total": CartService._format(grand_total),
        }

    @staticmethod
    def _calculate_discount(sub_total, discount_obj):

        if discount_obj.discount_type == "PERCENTAGE":
            discount = sub_total * (discount_obj.value / Decimal("100"))
        else:
            discount = discount_obj.value

        return discount.quantize(Decimal("0.01"), rounding=ROUND_DOWN)

    @staticmethod
    def _truncate(value):
        return value.quantize(Decimal("0.01"), rounding=ROUND_DOWN)

    @staticmethod
    def _format(value):
        return f"{value:.2f}"
