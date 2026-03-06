from django.template.loader import get_template
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
import logging
from order.models import OrderItems

logger = logging.getLogger(__name__)


class OrderEmailService:

    def send_order_email(self, order):

        user = order.user
        order_items = OrderItems.objects.filter(
            order=order, is_delete=False
        ).select_related("product", "product_varient")

        delivery_date = (order.created_at + timedelta(days=2)).strftime("%b %d %Y")

        all_order = []

        for item in order_items:

            image = None
            if item.product_varient and hasattr(item.product_varient, "image"):
                image = item.product_varient.image

            all_order.append(
                {
                    "product_image": image,
                    "product_name": item.product.title,
                    "quantity": item.quantity,
                    "total_price": item.total_price,
                    "price": item.price,
                    "variant_label": getattr(item.product_varient, "name", ""),
                }
            )

        context = {
            "first_name": user.first_name,
            "order_date": order.created_at,
            "delivery_at": delivery_date,
            "order_id": order.order_id,
            "ordered": all_order,
            "total_price": round(order.total_price, 2),
            "address": order.address,
            "delivery_charge": order.delivery_charge,
        }

        # Subscription Handling
        if order.is_subscribed:
            next_billing = order.created_at + timedelta(days=30)

            context.update(
                {
                    "next_billing": next_billing.strftime("%d-%m-%Y"),
                    "start_date": order.created_at.strftime("%d-%m-%Y"),
                }
            )

            template_path = "subscription_email.html"
        else:
            template_path = "regular_email.html"

        template = get_template(template_path)
        html_content = template.render(context)

        send_mail(
            subject="Order Successfully Placed",
            message="Order Purchased",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False,
            html_message=html_content,
        )
