from django.db import models
from django.db.models import DecimalField, QuerySet
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth.models import User
from typing import Dict, Optional, List


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
    stock_product: Stock = models.ForeignKey(Stock, on_delete=models.CASCADE, default=1)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} of {self.stock_product.product_instance.name}"

    @property
    def get_item_name(self) -> str:
        # Допустим, в характеристиках продукта есть цена
        rc: str = self.stock_product.product_instance.name

        return rc

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
    def get_total_price(self) -> float:
        price: DecimalField = self.stock_product.price

        return float(price) * int(self.quantity)

    @property
    def get_image(self):
        image = self.stock_product.imagesinstance_set.all()[0]

        return image.image.url

    @property
    def get_property_list(self) -> Dict[str, str]:
        properties: QuerySet[PropertyInstance] = self.stock_product.product_instance.propertyinstance_set.all()
        rc: Dict[str, str] = {}

        for prop in properties:
            key = str(prop.property_type_id.name)
            value = str(prop.value)

            rc[key] = value

        return rc

# --------------------
# Модели для оплаты
# --------------------

# Таблица для хранения кода валют
class CurrencyCode(models.Model):
    name = models.CharField(max_length=50, null=False)
    code = models.IntegerField(null=False) # Согласно ISO 4217

    def __str__(self):
        return f"Currency {self.id} - {self.name}"

# Модель по типам оплаты
class PaymentType(models.Model):
    name = models.CharField(max_length=50, null=False) # CБП/карта/наличка

    def __str__(self):
        return f"{self.name}"

# Таблица ставок на итоговую цену заказа
class PaymentRate(models.Model):
    payment_type = models.ForeignKey(PaymentType, on_delete=models.CASCADE, null=False, related_name='rate')
    rate = models.FloatField(max_length=25, null=False)

    def __str__(self):
        return f"Тип: {self.payment_type} | Ставка: {self.rate}"
# --------------------


# --------------------
# Модели заказов
# --------------------

class OrderStatus(models.Model):
    name = models.CharField(max_length=20,  null=False)

    def __str__(self):
        return f"{self.name}"


class TimeStampedModel(models.Model):
    """Абстрактный базовый класс, который добавляет поля created_at и updated_at к моделям"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: abstract = True


# Таблица для хранения заказов пользователя
class Order(TimeStampedModel):
    "Заказ после успешной оплаты"
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    customer_name = models.CharField(max_length=50, null=False)
    customer_phone = models.CharField(max_length=50, null=False)
    customer_email = models.CharField(max_length=50, null=False)
    customer_address = models.CharField(max_length=50, null=True)
    is_delivery = models.BooleanField(null=False)
    currency_code = models.ForeignKey(CurrencyCode, on_delete=models.CASCADE, null=False)
    total_price = models.IntegerField(null=False)
    # TODO: Указывает не Московское время
    # created_at = models.DateTimeField(auto_now_add=True, null=False)
    payment_type = models.ForeignKey(PaymentType, on_delete=models.CASCADE, null=False)
    status = models.ForeignKey(OrderStatus, null=False, on_delete=models.CASCADE)   # Здесь возможно три варианта: # pending, paid, canceled
    acquiring_order_id = models.CharField(max_length=36) # Номер заказа в платёжной системе. Уникален в пределах системы.
    def __str__(self):
        return f"Заказ {self.id} | Статус: {self.status} | Итоговая сумма: {self.total_price} | Создан: {self.created_at} | Обновлен: {self.updated_at}"

    @property
    def get_total_price(self) -> float:
        rc: float = self.total_price / 100

        return round(rc, 2)


#Cоздание таблицы OrderItem для хранения состава заказы
class OrderItem(models.Model):
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE, null=False)
    stock_data = models.JSONField(verbose_name="stock data", null=False)
    quantity = models.IntegerField(null=False)
    price = models.IntegerField(null=False)
    discount = models.FloatField(null=False)

    @property
    def unpack_properties_stock_data(self) -> str:
        string_list = [str(key) + ': ' + str(value) + ', ' for key, value in self.stock_data.get('properties').items()]
        string_stock_data: str = ''

        for element in string_list:
            string_stock_data += element

        return string_stock_data
# --------------------