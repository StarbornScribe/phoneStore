from django.contrib import admin

from .models import ProductType, ProductInstance, PropertyType, PropertyInstance
admin.site.register(ProductType)
admin.site.register(ProductInstance)
admin.site.register(PropertyType)
admin.site.register(PropertyInstance)
