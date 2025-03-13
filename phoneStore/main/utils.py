"""
Зачем нужен?
Модуль utils.py содержит вспомогательные функции, которые:
- Не зависят от бизнес-логики приложения.
- Являются общими и могут использоваться в разных частях приложения.
- Не взаимодействуют напрямую с базой данных или внешними сервисами.

Что содержит?
- Утилиты для работы с данными (например, форматирование строк, дат, чисел).
- Вспомогательные функции для работы с файлами, JSON, XML и т.д.
- Общие функции, которые не зависят от контекста приложения.
"""

import requests
from typing import Dict, Any, List

from django.core.mail import EmailMessage
from phoneStore.settings import EMAIL_HOST_USER
from django.template.loader import render_to_string

from main.models import Order, OrderItem

# TODO: Текущие функции нужно перенести в services.py
def send_html_email_from_store(order_object: Order, order_items: List[OrderItem], to_email, template_name):
    subject: str = f'Айфон-на-Дону. Заказ №{order_object.pk}'
    email_content: Dict[str, Any] = {
        'order_number': order_object.pk,
        'order_item_list': order_items,
        # TODO: Думаю лучше создать у модели метод конвертации в рубли
        'order_total_price': order_object.get_total_price,
        'customer_name': order_object.customer_name,
        'customer_phone': order_object.customer_phone,
        'customer_email': order_object.customer_email,
        'is_delivery': 'Да' if order_object.is_delivery == True else 'Нет',
        'customer_address': order_object.customer_address
    }

    # Рендеринг HTML-шаблона в строку
    html_message = render_to_string(template_name, email_content)

    # # Создание текстовой версии письма (опционально)
    # plain_message = strip_tags(html_message)

    # Создание объекта EmailMessage
    email = EmailMessage(
        subject=subject,
        body=html_message,  # Тело письма в HTML
        from_email=EMAIL_HOST_USER,  # Отправитель
        to=[to_email],  # Получатель
    )

    # Указываем, что письмо содержит HTML
    email.content_subtype = "html"

    # Отправка письма
    email.send()


def send_request_for_alfabank(json_data: Dict[str, str], end_point: str) -> Dict[str, str]:
    alfa_api_url: str = 'https://alfa.rbsuat.com/payment'

    response = requests.post(url=alfa_api_url + end_point, data=json_data)

    response_data: Dict[str, str] = response.json()

    return response_data
