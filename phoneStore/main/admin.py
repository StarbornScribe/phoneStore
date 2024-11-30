from dataclasses import field

from django.contrib import admin

from .models import ProductType, ProductInstance, PropertyType, PropertyInstance, ImagesInstance, Cart, CartItem, Stock

admin.site.register(ProductType)
admin.site.register(ProductInstance)
admin.site.register(PropertyType)
admin.site.register(PropertyInstance)
admin.site.register(ImagesInstance)
# admin.site.register(Stock)

# Модели корзины
# -------------
admin.site.register(Cart)
admin.site.register(CartItem)
# -------------


class GalleryInline(admin.TabularInline):
    fk_name = 'image_instance_id'
    model = ImagesInstance


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    inlines = [GalleryInline,]


# @admin.register(PropertyInstance)
# class PropertyInstanceAdmin(admin.ModelAdmin):
#     list_display = [field.name for field in PropertyInstance._meta.get_fields()]