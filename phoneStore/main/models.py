from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth.models import User
import uuid


class ProductType(models.Model):
    # Данный класс описывает тип продукта (телефон, планшет и т.д)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class ProductInstance(models.Model):
    # В данной таблице есть поле id, оно автоматически создается Django
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
    # Описывает какие названия характеристик могут быть у продукта (вес, ширина, высота и.т.д)
    product_type_id = models.ForeignKey(ProductType, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} для {self.product_type_id.name}"


class PropertyInstance(models.Model):
    # Задаёт значение характеристики конкретного продукта (вес равный 10, операционка iOS и т.д)
    product_instance_id = models.ForeignKey(ProductInstance, on_delete=models.CASCADE)
    property_type_id = models.ForeignKey(PropertyType, on_delete=models.CASCADE)
    value = models.CharField(max_length=100)
    # image_instance_id = models.ForeignKey(ImagesInstance, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.property_type_id.name}: {self.value} ({self.product_instance_id.name})"

# ---------
# Склад
# ---------


class Stock(models.Model):
    product_instance = models.ForeignKey(ProductInstance, on_delete=models.CASCADE)
    property_instances = models.ManyToManyField(PropertyInstance, blank=True)
    quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        properties = ", ".join([f"{prop.property_type_id.name}: {prop.value}" for prop in self.property_instances.all()])
        return f"{self.product_instance.name} [{properties}] - {self.quantity} шт."

    def is_in_stock(self):
        """Проверяет, есть ли товар в наличии."""
        return self.quantity > 0


class ImagesInstance(models.Model):
    image_instance_id = models.ForeignKey(Stock, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='media/')

    def __str__(self):
        return f"Image for {self.image_instance_id.product_instance}"

# ---------
# Корзина
# ---------


class Cart(models.Model):
    """
    Хранит корзину пользователя.
    Если пользователь не авторизован, корзина связывается с идентификатором сессии.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Связь с пользователем
    session_id = models.CharField(max_length=255, null=True, blank=True)  # Для анонимных пользователей
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Добавляем аннотацию типа для user (Optional[User] означает, что user может быть None)
        user_display = self.user.username if self.user else "Anonymous"
        return f"Cart {self.id} for {user_display}"


class CartItem(models.Model):
    """
    Описывает конкретные товары и их количество в корзине.
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    # product = models.ForeignKey(ProductInstance, on_delete=models.CASCADE)
    stock_product: Stock = models.ForeignKey(Stock, on_delete=models.CASCADE, default=1)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.quantity} of {self.stock_product.product_instance.name}"

    @property
    def get_memory_size(self):
        # Допустим, в характеристиках продукта есть цена
        memory_size = self.stock_product.product_instance.propertyinstance_set.filter(property_type_id__name='Встроенная память').first()
        if memory_size is None:
            rc = " "
        else:
            rc = memory_size.value

        return rc

    @property
    def get_color(self):
        color = self.stock_product.product_instance.propertyinstance_set.filter(property_type_id__name='Цвет').first()
        if color is None:
            rc = " "
        else:
            rc = color.value
        return rc

    @property
    def get_total_price(self):
        price = self.stock_product.price
        return price * self.quantity

    @property
    def get_image(self):
        image = self.stock_product.imagesinstance_set.all()[0]
        return image.image.url

class Order(models.Model):
    "Заказ после успешной оплаты"
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default="pending") # Здесь возможно три варианта: # pending, paid, canceled
    order_id = models.UUIDField(default=uuid.uuid4, unique=True)

    def __str__(self):
        return f"Order {self.order_id} - {self.status}"

