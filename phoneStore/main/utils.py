import requests
from typing import Dict

from django.core.mail import EmailMessage
from phoneStore.settings import EMAIL_HOST_USER
from django.template.loader import render_to_string


def send_rendered_html_email(subject, to_email, context, template_name):
    # Рендеринг HTML-шаблона в строку
    html_message = render_to_string(template_name, context)

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
