from celery import shared_task
from django.db import transaction
import logging
from order.models import Order
from order.order_email_service import OrderEmailService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def send_order_email(self, order_id):

    try:
        order = Order.objects.select_related("user").get(id=order_id)
        OrderEmailService().send_order_email(order)
        logger.info(f"Order email sent successfully for Order {order.order_id}")
    except Exception as exc:
        logger.error(f"Email sending failed: {str(exc)}")
        raise self.retry(exc=exc)
