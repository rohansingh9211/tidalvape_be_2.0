import requests
import logging
from django.conf import settings
from django.db import transaction
from order.models import Order
logger = logging.getLogger(__name__)


class ShopifyOrderBoard:

    def __init__(self):
        self.base_url = f"https://{settings.SHOPIFY_STORE_DOMAIN}/admin/api/{settings.SHOPIFY_API_VERSION}"
        self.headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": settings.SHOPIFY_ADMIN_TOKEN
        }

    def create_order(self, order_id: int):

        order = Order.objects.select_related("user").prefetch_related(
            "order_item__product",
            "order_item__product_varient"
        ).get(id=order_id)

        # Prevent duplicate push
        if order.shopify_order_id:
            logger.info("Order already pushed to Shopify.")
            return order.shopify_response

        payload = self._build_payload(order)

        url = f"{self.base_url}/orders.json"

        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=20
            )
            response.raise_for_status()

            data = response.json()

            # Save Shopify response safely
            with transaction.atomic():
                order.shopify_order_id = data["order"]["id"]
                order.shopify_response = data
                order.save(update_fields=["shopify_order_id", "shopify_response"])

            logger.info(f"Shopify order created: {order.shopify_order_id}")
            return data

        except requests.exceptions.RequestException as e:
            logger.error(f"Shopify Order Error: {str(e)}")
            return None

    def _build_payload(self, order):
        line_items = []
        for item in order.order_item.filter(is_delete=False):

            if not item.product_varient or not item.product_varient.id:
                raise Exception(
                    f"Missing Shopify variant ID for product {item.product.title}"
                )

            line_items.append({
                "variant_id": item.product_varient.id,
                "quantity": item.quantity,
            })

        final_amount = order.total_price + order.delivery_charge

        return {
            "order": {
                "line_items": line_items,

                "customer": {
                    "email": order.user.email,
                    "first_name": order.user.first_name or "Guest",
                    "last_name": order.user.last_name or "User",
                },

                "billing_address": {
                    "address1": order.address,
                    "country": "United Kingdom",
                    "first_name": order.user.first_name or "Guest",
                    "last_name": order.user.last_name or "User",
                },

                "shipping_address": {
                    "address1": order.address,
                    "country": "United Kingdom",
                    "first_name": order.user.first_name or "Guest",
                    "last_name": order.user.last_name or "User",
                },

                "transactions": [
                    {
                        "kind": "sale",
                        "status": "success",
                        "amount": str(final_amount)
                    }
                ],

                "shipping_lines": [
                    {
                        "title": "Delivery Charge",
                        "price": str(order.delivery_charge)
                    }
                ],

                "currency": "GBP",
                "financial_status": "paid",
                "note": f"Internal Order ID: {order.order_id}",
                "send_receipt": False,
                "send_fulfillment_receipt": False
            }
        }