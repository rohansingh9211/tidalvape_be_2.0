import os
import requests
import pandas as pd
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils.text import slugify
from django.utils import timezone

from product.models import Product, ProductImage, ProductOption, ProductTag, ProductType, ProductVariant, Vendor

class Command(BaseCommand):
    help = "Import products from Shopify Excel file"

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str, help="Path to Excel file")

    def handle(self, *args, **kwargs):
        file_path = kwargs["file_path"]
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        for index, row in df.iterrows():

            handle = row.get("Handle")
            if not handle:
                continue

            product, created = Product.objects.get_or_create(
                handle=handle,
                defaults={
                    "title": row.get("Title"),
                    "body_html": row.get("Body (HTML)"),
                    "status": row.get("Status"),
                },
            )

            # ------------------------
            # Vendor
            # ------------------------
            vendor_name = row.get("Vendor")
            if vendor_name:
                vendor, _ = Vendor.objects.get_or_create(name=vendor_name)
                product.vendor = vendor

            # ------------------------
            # Product Type
            # ------------------------
            product_type_name = row.get("Type")
            if product_type_name:
                product_type, _ = ProductType.objects.get_or_create(
                    name=product_type_name
                )
                product.product_type = product_type

            product.save()

            # ------------------------
            # Tags (comma separated)
            # ------------------------
            tags = row.get("Tags")
            if tags:
                tag_list = [tag.strip() for tag in tags.split(",")]
                for tag_name in tag_list:
                    tag_obj, _ = ProductTag.objects.get_or_create(name=tag_name)
                    product.tags.add(tag_obj)

            # ------------------------
            # Product Options
            # ------------------------
            for i in range(1, 4):
                option_name = row.get(f"Option{i} Name")
                if option_name:
                    ProductOption.objects.get_or_create(
                        product=product,
                        name=option_name,
                        position=i,
                    )

            # ------------------------
            # Create Variant
            # ------------------------
            variant_title = row.get("Option1 Value") or "Default"

            ProductVariant.objects.create(
                product=product,
                title=variant_title,
                price=row.get("Variant Price") or 0,
                compare_at_price=row.get("Variant Compare At Price"),
                sku=row.get("Variant SKU"),
                barcode=row.get("Variant Barcode"),
                inventory_policy=row.get("Variant Inventory Policy"),
                fulfillment_service=row.get("Variant Fulfillment Service"),
                grams=row.get("Variant Grams") or 0,
                inventory_management=row.get("Variant Inventory Tracker"),
                requires_shipping=row.get("Variant Requires Shipping") == True,
                taxable=row.get("Variant Taxable") == True,
                option1=row.get("Option1 Value"),
                option2=row.get("Option2 Value"),
                option3=row.get("Option3 Value"),
                weight_unit=row.get("Variant Weight Unit"),
            )

            # ------------------------
            # Image
            # ------------------------
            image_url = row.get("Variant Image")
            if image_url:
                if not ProductImage.objects.filter(product=product).exists():
                    try:
                        response = requests.get(image_url)
                        if response.status_code == 200:
                            image_file = ContentFile(response.content)
                            file_name = image_url.split("/")[-1]

                            ProductImage.objects.create(
                                product=product,
                                image=image_file,
                                alt=row.get("Image Alt Text"),
                                position=row.get("Image Position"),
                            ).image.save(file_name, image_file, save=True)

                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f"Image error: {e}")
                        )

        self.stdout.write(self.style.SUCCESS("Import completed successfully!"))