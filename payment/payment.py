from django.db import transaction as db_transaction
from django.utils import timezone
from decimal import Decimal
from account.models import Address, User, UserLoyalty
from common.response import StandardAPIResponse
from common.utils.gerneric_utils import generate_unique_order_id
from order.models import Order, OrderItems, Subscription
from order.serializers import UserOrderSerializer
from payment.models import Transaction
from product.models import Product, ProductDeal, ProductVariant
from shop.models import Discount, ReedemCode, UserReedem
from django.contrib.auth.hashers import make_password
from rest_framework import status
from decimal import Decimal, ROUND_DOWN
from django.db.models import F

from shopify_operator.shopify_order_board import ShopifyOrderBoard
from order.tasks.order_email import send_order_email
from tidalvape_be import settings

DELIVERY_THRESHOLD = Decimal(settings.DELIVERY_THRESHOLD)
DELIVERY_CHARGE = Decimal(settings.DELIVERY_CHARGE)

def get_user_address_detail(data):
    user = User.objects.get(email=data['email'])
    address = Address.objects.get(id=data['address'])

    return {
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "phone_number": user.phone_number,
        "address": address.flat_name,
        "zip_code": address.zip_code,
        "city": address.city,
        "postal_code": address.zip_code,
        "admin_area": address.landmark
    }

def create_transaction(request_data):

    try:
        with db_transaction.atomic():
            user_detail = get_user_address_detail(request_data)
            user, _ = User.objects.get_or_create(
                email=user_detail['email'],
                defaults={
                    "password": make_password(user_detail['email'])
                }
            )
            transaction_obj = Transaction.objects.select_for_update().get(
                cyber_transactionid=request_data['authenticationTransactionId']
            )

            order_data = find_total_calculation(request_data)            
            address_text = build_address_text(
                request_data['delivery_type'],
                user_detail
            )

            order = Order.objects.create(
                order_id=generate_unique_order_id(),
                user=user,
                transaction=transaction_obj,
                delivery_charge=order_data['delivery_charge'],
                total_price=order_data['grand_total'],
                sub_total_price=order_data['sub_total'],
                discount_amount=order_data['discount_amount'],
                status='SUCCESS',
                address=address_text,
                payload=str(request_data),
                is_subscribed=request_data.get('is_subscription', False)
            )

            create_order_items(order, order_data)
            
            if request_data.get('is_subscription'):
                handle_subscription(order, request_data, order_data, user, address_text)
            else:
                handle_promo_code(request_data, user)

        # Outside atomic block
        # send_order_email.delay(order.id)
        # ShopifyOrderBoard().create_order(order.id)
        UserLoyalty.objects.filter(user=user).update(
            points=F('points') + 1
        )
        return StandardAPIResponse( UserOrderSerializer(order).data, status=status.HTTP_201_CREATED)

    except Exception as e:
        return StandardAPIResponse({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

def build_address_text(delivery_type, user_detail):
    if delivery_type == "standard":
        return f"{user_detail['address']} {user_detail['zip_code']} United Kingdom"

    return "Tidal Vape Chandler's Ford, 8-9 Fryern Arcade, Winchester Road, Chandler's Ford, Eastleigh, SO53 2DP"

def create_order_items(order, order_data):
    items = []

    for item in order_data.get('order_item', []):
        items.append(
            OrderItems(
                product=item.get('product'),
                order=order,
                quantity=item['quantity'],
                price=item.get('price'),
                total_price=item.get('sub_total'),
                product_varient=item.get("variant"),
            )
        )

    OrderItems.objects.bulk_create(items)


def handle_subscription(order, request_data, order_data, user, address_text):
    for order_itm in order_data.get('order_item', []):
        Subscription.objects.create(
            user=user,
            order=order,
            product = order_itm.get('product'),
            product_varient = order_itm.get('variant'),
            days=request_data.get('subscription_days'),
            delivery_charge=order_data['delivery_charge'],
            price=order_itm['price'],
            quantity=order_itm['quantity'],
            discount=order_data['discount_amount'],
            total_price=order_data['grand_total'],
            address=address_text,
            sub_total=order_data['sub_total']
        )


def find_total_calculation(request_data: dict):
    try:
        cart_items = request_data.get("cart_product", [])
        subscription = request_data.get("is_subscription", False)
        loyalty_discount_id = request_data.get("loyality_discount")

        if not cart_items:
            return {
                "sub_total": "0.00",
                "discount_amount": "0.00",
                "delivery_charge": "0.00",
                "grand_total": "0.00",
                "order_item": []
            }

        product_ids = [item["product"] for item in cart_items]
        variant_ids = [
            item["variant"]["id"]
            for item in cart_items
            if item.get("variant") and item["variant"].get("id")
        ]
        deal_ids = [item.get("deal_id") for item in cart_items if item.get("deal_id")]
        
        products = {p.id: p for p in Product.objects.filter(id__in=product_ids)}
        variants = {v.id: v for v in ProductVariant.objects.filter(id__in=variant_ids)}
        deals = {d.id: d for d in ProductDeal.objects.filter(id__in=deal_ids)}
        
        order_cart = []
        sub_total = Decimal("0.00")

        for item in cart_items:
            product = products.get(item["product"])
            variant = variants.get(item["variant"]["id"])
            deal = deals.get(item.get("deal_id"))
            if not product:
                continue

            quantity = Decimal(str(item.get("quantity", 1)))
            price = variant.price if variant else product.price

            # Apply deal if exists
            if deal and deal.deal_price > 0:
                price = price - Decimal(str(deal.deal_price))

            item_total = price * quantity

            if item_total < 0:
                item_total = Decimal("0.00")

            sub_total += item_total

            order_cart.append({
                "product": product,
                "variant": variant,
                "quantity": quantity,
                "price": truncate(price),
                "sub_total": truncate(item_total),
                "deal": deal
            })

        sub_total = truncate(sub_total)

        subscription_discount = None
        loyalty_discount = None

        if subscription:
            subscription_discount = Discount.objects.filter(
                discount_category="SUBSCRIPTION",
                is_active=True
            ).first()

        if loyalty_discount_id:
            loyalty_discount = Discount.objects.filter(
                id=loyalty_discount_id,
                discount_category="LOYALTY",
                is_active=True
            ).first()

        subscription_discount_amt = Decimal("0.00")
        loyalty_discount_amt = Decimal("0.00")
        
        if subscription_discount:
            subscription_discount_amt = calculate_discount(
                sub_total, subscription_discount
            )

        if loyalty_discount:
            loyalty_discount_amt = calculate_discount(
                sub_total, loyalty_discount
            )
        
        total_discount = subscription_discount_amt + loyalty_discount_amt
        total_discount = truncate(total_discount)
        
        delivery_charge = (
            DELIVERY_CHARGE
            if sub_total < DELIVERY_THRESHOLD
            else Decimal("0.00")
        )

        grand_total = sub_total - total_discount + delivery_charge
        grand_total = truncate(grand_total)

        # ---------------------------------
        # Final Response
        # ---------------------------------
        return {
            "sub_total": format_amount(sub_total),
            "discount_amount": format_amount(total_discount),
            "delivery_charge": format_amount(delivery_charge),
            "grand_total": format_amount(grand_total),
            "order_item": order_cart 
        }

    except Exception as e:
        return {
            "error": str(e),
            "sub_total": "0.00",
            "discount_amount": "0.00",
            "delivery_charge": "0.00",
            "grand_total": "0.00",
            "order_item": []
        }
        
def handle_promo_code(request_data, user):
    promo_id = request_data.get("promo_code")
    if promo_id:
        reedem_code = ReedemCode.objects.filter(id=promo_id).first()
        if reedem_code:
            UserReedem.objects.create(user=user, reedem_code=reedem_code)

def truncate(value):
    return value.quantize(Decimal("0.01"), rounding=ROUND_DOWN)

def format_amount(value):
    return f"{truncate(value):.2f}"

def calculate_discount(sub_total, discount_obj):
    if discount_obj.discount_type == "PERCENTAGE":
        discount = sub_total * (discount_obj.value / Decimal("100"))
    else:
        discount = discount_obj.value

    return truncate(discount)