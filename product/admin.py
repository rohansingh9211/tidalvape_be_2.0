from django.contrib import admin
from .models import (Product, ProductImage, ProductOption, ProductType, ProductVariant, Vendor)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "title",
        "vendor",
        "product_type",
        "status",
        "published_scope",
        "display_tags",
        "published_at",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "status",
        "published_scope",
        "vendor",
        "product_type",
        "published_at",
        "created_at",
    )

    search_fields = (
        "title",
        "handle",
        "id",
        "vendor__name",
        "product_type__name",
    )

    filter_horizontal = ("tags",)

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )

    ordering = ("-created_at",)
    list_per_page = 25

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("vendor", "product_type").prefetch_related(
            "tags"
        )

    @admin.display(description="Tags")
    def display_tags(self, obj):
        return ", ".join(tag.name for tag in obj.tags.all())


admin.site.register(Vendor)
admin.site.register(ProductType)
admin.site.register(ProductVariant)
admin.site.register(ProductOption)
admin.site.register(ProductImage)