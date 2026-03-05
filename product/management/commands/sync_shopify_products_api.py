import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.dateparse import parse_datetime
from django.core.files.base import ContentFile


from product.models import (
    Vendor,
    ProductType,
    ProductTag,
    Product,
    ProductVariant,
    ProductOption,
    ProductImage,
)


class Command(BaseCommand):
    help = "Sync products from Shopify API"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("Starting Shopify product sync..."))

        shop_url = settings.SHOPIFY_STORE_DOMAIN
        access_token = settings.SHOPIFY_ADMIN_TOKEN
        version = settings.SHOPIFY_API_VERSION

        url = f"https://{shop_url}/admin/api/{version}/products.json"

        headers = {
            "X-Shopify-Access-Token": access_token,
            "Content-Type": "application/json",
        }

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            self.stdout.write(self.style.ERROR("Failed to fetch products"))
            return

        products_data = response.json().get("products", [])

        for product_data in products_data:
            self.sync_product(product_data)

        self.stdout.write(self.style.SUCCESS("Shopify product sync completed!"))

    def sync_product(self, data):

        # =========================
        # Vendor (NO Shopify ID)
        # =========================
        vendor = None
        if data.get("vendor"):
            vendor_name = data["vendor"].strip()

            vendor = Vendor.objects.filter(name=vendor_name).first()

            if not vendor:
                vendor = Vendor.objects.create(
                    name=vendor_name
                )

        # =========================
        # Product Type (NO Shopify ID)
        # =========================
        product_type = None
        if data.get("product_type"):
            pt_name = data["product_type"].strip()

            product_type = ProductType.objects.filter(name=pt_name).first()

            if not product_type:
                product_type = ProductType.objects.create(
                    name=pt_name
                )

        # =========================
        # Product (USE Shopify ID)
        # =========================
        product, _ = Product.objects.update_or_create(
            id=data["id"],  # 🔥 Shopify product ID
            defaults={
                "handle": data.get("handle"),
                "title": data.get("title"),
                "body_html": data.get("body_html"),
                "vendor": vendor,
                "product_type": product_type,
                "status": data.get("status"),
                "published_scope": data.get("published_scope"),
                "published_at": parse_datetime(data.get("published_at"))
                if data.get("published_at")
                else None,
                "template_suffix": data.get("template_suffix"),
            },
        )

        # =========================
        # Tags (NO Shopify ID)
        # =========================
        product.tags.clear()
        tags_string = data.get("tags", "")

        if tags_string:
            for tag_name in tags_string.split(","):
                tag_name = tag_name.strip()

                tag = ProductTag.objects.filter(name=tag_name).first()

                if not tag:
                    tag = ProductTag.objects.create(
                        name=tag_name
                    )

                product.tags.add(tag)

        # =========================
        # Variants (USE Shopify ID)
        # =========================
        for variant in data.get("variants", []):
            ProductVariant.objects.update_or_create(
                id=variant["id"],  # 🔥 Shopify variant ID
                defaults={
                    "product": product,
                    "inventory_item_id": variant.get("inventory_item_id"),
                    "title": variant.get("title"),
                    "price": variant.get("price") or 0,
                    "position": variant.get("position"),
                    "inventory_policy": variant.get("inventory_policy"),
                    "compare_at_price": variant.get("compare_at_price"),
                    "option1": variant.get("option1"),
                    "option2": variant.get("option2"),
                    "option3": variant.get("option3"),
                    "taxable": variant.get("taxable"),
                    "barcode": variant.get("barcode"),
                    "fulfillment_service": variant.get("fulfillment_service"),
                    "grams": variant.get("grams"),
                    "inventory_management": variant.get("inventory_management"),
                    "requires_shipping": variant.get("requires_shipping"),
                    "sku": variant.get("sku"),
                    "weight": variant.get("weight"),
                    "weight_unit": variant.get("weight_unit"),
                    "inventory_quantity": variant.get("inventory_quantity"),
                    "image_id": variant.get("image_id"),
                },
            )

        # =========================
        # Options
        # =========================
        for option in data.get("options", []):
            ProductOption.objects.update_or_create(
                id=option["id"],   # 🔥 Shopify option ID
                defaults={
                    "product": product,
                    "name": option.get("name"),
                    "position": option.get("position"),
                },
            )

        # =========================
        # Images (USE Shopify ID)
        # =========================
        for image in data.get("images", []):
            image_obj, created = ProductImage.objects.update_or_create(
                id=image["id"],  # 🔥 Shopify image ID
                defaults={
                    "product": product,
                    "position": image.get("position"),
                    "alt": image.get("alt"),
                    "width": image.get("width"),
                    "height": image.get("height"),
                },
            )

            # Download image only if newly created
            if created and image.get("src"):
                img_response = requests.get(image["src"])
                if img_response.status_code == 200:
                    file_name = image["src"].split("/")[-1]
                    image_obj.image.save(
                        file_name,
                        ContentFile(img_response.content),
                        save=True,
                    )