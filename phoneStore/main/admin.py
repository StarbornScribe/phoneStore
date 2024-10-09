from django.contrib import admin

from .models import ProductType, ProductInstance, PropertyType, PropertyInstance, ImagesInstance

admin.site.register(ProductType)
# admin.site.register(ProductInstance)
admin.site.register(PropertyType)
admin.site.register(PropertyInstance)
admin.site.register(ImagesInstance)


class GalleryInline(admin.TabularInline):
    fk_name = 'image_instance_id'
    model = ImagesInstance

@admin.register(ProductInstance)
class ProductAdmin(admin.ModelAdmin):
    inlines = [GalleryInline,]
