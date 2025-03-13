"""
Зачем нужен?
Сервисный слой (services.py) используется для инкапсуляции бизнес-логики приложения. Он отвечает за выполнение операций, которые:
- Взаимодействуют с базой данных.
- Реализуют сложную бизнес-логику.
- Координируют работу нескольких моделей или компонентов.

Что содержит?
- Функции, которые выполняют запросы к базе данных.
- Логику, связанную с обработкой данных (например, расчеты, преобразования).
- Взаимодействие с внешними API или сторонними сервисами.
- Логику, которая не относится напрямую к представлениям (views) или моделям (models).
"""
from typing import Dict, Any, List
from django.db.models import QuerySet

from main.models import Order, OrderItem, OrderStatus, Cart, CartItem, CurrencyCode, PaymentType


def get_order_items(order_object: Order) -> List[OrderItem]:
    order_item_list: List[OrderItem] = [item for item in OrderItem.objects.filter(order_id=order_object)]

    return order_item_list

def create_order_in_db(cart_object: Cart, order_front_data: Dict[str, str]) -> Order:
    """
    Создает заказ в базе данных на основе данных корзины и фронтенда.

    :param cart_object: Объект корзины.
    :param order_front_data: Данные с фронтенда (имя, телефон, email, адрес, способ оплаты и т.д.).
    :return: Созданный объект заказа
    """
    cart_items: QuerySet[CartItem] = CartItem.objects.filter(cart=cart_object)
    currency_code: str = CurrencyCode.objects.filter(name='RUB').first()
    if not currency_code:
        raise ValueError("Валюта 'RUB' не найдена в базе данных.")

    payment_type_object: PaymentType = PaymentType.objects.filter(name=order_front_data['payment_type']).first()
    if not payment_type_object:
        raise ValueError("Указанный способ оплаты не найден.")

    try:
        # Необходимо парсить во float, так как с фронта цена приходит в виде строки
        order_total_price: float = float(order_front_data['total_price'])
        order_total_price: int = int(order_total_price) * 100
    except (ValueError, TypeError):
        raise ValueError('Некорректное значение total_price')

    status: OrderStatus = OrderStatus.objects.filter(name='pending').first()
    if not status:
        raise ValueError("Статус 'pending' не найден в базе данных.")

    order_object: Order = Order(
        customer_name=order_front_data['name'],
        customer_phone=order_front_data['phone'],
        customer_email=order_front_data['email'],
        customer_address=order_front_data['location'],
        # TODO: Необходимо сделать логику под доставку
        is_delivery=False,
        currency_code=currency_code,
        total_price=order_total_price,
        payment_type=payment_type_object,
        status=OrderStatus.objects.filter(name='pending').first()
    )
    order_object.save()

    order_items = []
    for item in cart_items:
        properties_dict: Dict[str, str] = item.get_property_list
        order_items.append(
            OrderItem(
                order_id=order_object,
                stock_data={
                    'product_name': item.get_item_name,
                    'properties': properties_dict
                },
                quantity=item.quantity,
                price=item.get_total_price,
                discount=0.0
            )
        )

    # Сохраняем все товары заказа одним запросом
    OrderItem.objects.bulk_create(order_items)

    return order_object
