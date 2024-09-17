from django.db import models
from django.urls import reverse
from django.utils.text import slugify




class ProductType(models.Model):
    # Данный класс описывает тип продукта (телефон, планшет и т.д)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class ProductInstance(models.Model):
    # Описывает какие конкретно модели продуктов могут быть (iphone 10, samsung galaxy 10 и.т.д)
    product_type_id = models.ForeignKey(ProductType, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True, blank=True, null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('phone-detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            # Automatically generate the slug from the name
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class PropertyType(models.Model):
    # Описывает какие названия характеристик могут быть у продукта продукта (вес, ширина, высота и.т.д)
    product_type_id = models.ForeignKey(ProductType, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class ImagesInstance(models.Model):
    image_instance_id = models.ForeignKey(ProductInstance, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='media/')


    def __str__(self):
        return f"Image for {self.image_instance_id.name}"





class PropertyInstance(models.Model):
    # Задаёт значение характеристики конкретного продукта (вес равный 10, операционка iOS и т.д)
    product_instance_id = models.ForeignKey(ProductInstance, on_delete=models.CASCADE)
    property_type_id = models.ForeignKey(PropertyType, on_delete=models.CASCADE)
    value = models.CharField(max_length=100)
    image_instance_id = models.ForeignKey(ImagesInstance, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'{self.property_type_id.name}: {self.value}'


