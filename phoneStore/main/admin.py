from dataclasses import field
from typing import List
from django import forms
from django.contrib import admin

from .models import ProductType, ProductInstance, PropertyType, PropertyInstance, ImagesInstance, Cart, CartItem, Stock

admin.site.register(ProductType)
# admin.site.register(ProductInstance)
# admin.site.register(PropertyType)
# admin.site.register(PropertyInstance)
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


@admin.register(ProductInstance)
class ProductInstanceAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


@admin.register(PropertyType)
class PropertyTypeAdmin(admin.ModelAdmin):
    list_display = ('product_type_id', 'name')
    list_filter = ['product_type_id']


@admin.register(PropertyInstance)
class PropertyInstanceAdmin(admin.ModelAdmin):
    list_display: List[str] = ['product_instance_id', 'property_type_id', 'value']
    list_filter: List[str] = ['product_instance_id']


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_filter: List[str] = ['product_instance', 'price']
    raw_id_fields: List[str] = ['property_instances']
    inlines = [GalleryInline,]


class CustomStockModelForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = '__all__'

    def __init__(self, product_instance, *args, **kwargs):
        super(CustomStockModelForm, self).__init__(*args, **kwargs)
        self.fields['property_instances'].queryset = PropertyInstance.objects.filter(product_instance_id__name=product_instance) # or something else


# @admin.register(PropertyInstance)
# class PropertyInstanceAdmin(admin.ModelAdmin):
#     list_display = [field.name for field in PropertyInstance._meta.get_fields()]
