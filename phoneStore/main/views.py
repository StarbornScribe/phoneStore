import json
import uuid
import requests
from typing import List, Any, Dict, Optional

from django.conf import settings
from django.http import JsonResponse
from typing import List, Any, Dict
from django.views.generic import DetailView
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.core.mail import send_mail
from phoneStore.settings import EMAIL_HOST_USER
from .models import ProductInstance, ProductType, PropertyType, PropertyInstance, ImagesInstance, Stock, Cart, CartItem, Order
from django.http import HttpResponseRedirect
from django.http import HttpRequest
from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.views.decorators.csrf import csrf_exempt
from .models import ProductInstance, PropertyInstance, ImagesInstance, Stock


def bootstrap_page_handler(request):
    # print("bootstrap_page_handler called")
    # pdb.set_trace()  # This will pause execution and allow you to inspect variables.
    return render(request, 'index.html')


def view_single_product(request, pk):
    product = get_object_or_404(ProductInstance, pk=pk)
    context = {
        'product': product,
    }
    return render(request, 'single-product-slider.html', context)


def view_single_product_alternative(request, pk):
    product = get_object_or_404(ProductInstance, pk=pk)
    context = {
        'product': product,
    }
    return render(request, 'single-product-tabstyle-2.html', context)


class PhoneDetailView(DetailView):
    model = ProductInstance
    template_name = 'single-product-tabstyle-2.html'

    def get_context_data(self, *args, **kwargs):
        slug_name: str = self.kwargs['slug']
        context = super(PhoneDetailView, self).get_context_data(*args, **kwargs)

        product_instance = ProductInstance.objects.get(slug=slug_name)

        context['object_name'] = product_instance
        context['object_image'] = ImagesInstance.objects.filter(image_instance_id__slug=slug_name)
        context['object_property'] = PropertyInstance.objects.filter(product_instance_id__slug=slug_name)

        # Извлекаем цену
        try:
            price_property = PropertyInstance.objects.get(
                product_instance_id=product_instance,
                property_type_id__name="Цена"
            )
            context['object_price'] = price_property.value
        except PropertyInstance.DoesNotExist:
            context['object_price'] = "Цена не указана"

        return context

  
def phones_catalog(request, product_type, product_name=None):
    if product_name:
        # Если задан product_name, фильтруем также по имени
        product_instances = ProductInstance.objects.filter(
            product_type_id__name=product_type,
            slug=product_name
        ).prefetch_related('propertyinstance_set__property_type_id')
    else:
        # Если product_name не задан, фильтруем только по типу продукта
        product_instances = ProductInstance.objects.filter(
            product_type_id__name=product_type
        ).prefetch_related('propertyinstance_set__property_type_id')

    image_instances: ImagesInstance = ImagesInstance.objects.all()

    # image_instances: ImagesInstance = ImagesInstance.objects.select_related('image_instance_id__product_type_id')
    context = {
        'product_instances': product_instances,
        'image_instances': image_instances,
    }

    return render(request, 'catalog.html', context)

# ---------
# Склад
# ---------

def product_detail_view(request, slug, stock_id):
    # Получаем объект ProductInstance по slug
    product_instance = get_object_or_404(ProductInstance, slug=slug)

    # Получаем конкретную запись Stock по ID
    stock = get_object_or_404(Stock, id=stock_id, product_instance=product_instance)

    # Подготовка данных для шаблона
    stock_data: Dict[str, Any] = {
        'product_type': str(product_instance.product_type_id),
        'name': product_instance.name,
        'quantity': stock.quantity,
        'price': float(stock.price),
        'properties': [
            {
                'name': prop.property_type_id.name,
                'value': prop.value
            }
            for prop in stock.property_instances.all()
        ],
        'images': [
            image.image.url
            for image in stock.imagesinstance_set.all()
        ]
    }

    context: Dict = {
        'product': product_instance,
        'stock_data': stock_data,
        'stock_id': stock_id
    }
    request.session['stock_data'] = stock_data

    return render(request, 'single-product-tabstyle-2.html', context)


def phones_catalog_thrid(request, product_type, product_name=None):
    # Базовый фильтр по типу продукта
    product_instances = ProductInstance.objects.filter(
        product_type_id__name=product_type
    )

    # TODO: Как временное решение сделал маппер для типов, чтобы выводить тип на русском языке в хлебных крошках
    product_type_mapper: Dict[str, str] = {
        'phones': 'Телефоны',
        'pads': 'Планшеты',
        'laptops': 'Ноутбуки',
        'headphones': 'Наушники',
        'accessories': 'Аксессуары'
    }

    # Если задано имя продукта (slug), фильтруем дополнительно по нему
    if product_name:
        product_instances = product_instances.filter(name=product_name)

    # Получаем только те товары, которые есть в наличии
    stocks = Stock.objects.filter(
        product_instance__in=product_instances,  # Привязываем Stock к выбранным ProductInstance
        quantity__gt=0  # Учитываем только товары в наличии
    ).select_related(
        'product_instance',  # Подтягиваем данные о продукте
        'product_instance__product_type_id'  # Подтягиваем данные о типе продукта
    ).prefetch_related(
        'property_instances',  # Подтягиваем свойства продукта
        'property_instances__property_type_id',  # Типы свойств
        'imagesinstance_set'  # Изображения через связанный ImageInstance
    )

    # Подготавливаем данные для отображения
    catalog_data = []
    for stock in stocks:
        # Для каждого товара собираем нужную информацию
        catalog_data.append({
            'product_name': stock.product_instance.name,
            'product_type': stock.product_instance.product_type_id.name,
            'stock_id': stock.id,
            'slug': stock.product_instance.slug,
            'quantity': stock.quantity,
            'price': stock.price,
            'properties': [
                {
                    'name': prop.property_type_id.name,
                    'value': prop.value
                }
                for prop in stock.property_instances.all()
            ],
            'images': [
                image.image.url
                for image in stock.imagesinstance_set.all()
            ],
            # TODO: Здесь есть косяк с тем, что если свойства Цвет не будет добавлено для продукта,
            #  вьюха упадёт с ошибкой
            'color': [prop for prop in stock.property_instances.all() if prop.property_type_id.name == 'Цвет'][0].value
        })

    # Словарь для формирования фильтра продуктов вверху страницы
    filter_catalog: List[Dict[str, Any]] = []
    names_list: List[str] = []

    for product_data in catalog_data:
        if product_data['product_name'] not in names_list:      # Проверка на уникальность
            names_list.append(product_data['product_name'])     # Добавляем значение product_name в список, чтобы проходила проверка на уникальность
            filter_catalog.append({
                'type': product_data['product_type'],
                'name': product_data['product_name'],
                'image': product_data['images'][0] if len(product_data['images']) != 0 else None, # Добавляем первое изображение продукта
                'slug': product_data['slug']
            })

            # filter_catalog['product_names'].append(product_data['product_name'])
            # filter_catalog['product_images'].append(product_data['images'][0]) # Добавляем первое изображение продукта

    # Формируем контекст для шаблона
    context = {
        'product_type_name': product_type_mapper[product_type] if product_type in product_type_mapper.keys() else product_type,
        'filter_catalog': filter_catalog,
        'catalog_data': catalog_data,  # Передаем готовые данные для отображения
        'product_type': product_type,  # Передаем тип продукта
        'product_name': product_name,  # Передаем конкретное имя продукта, если указано
    }
    return render(request, 'catalog.html', context)

# -------------------
# Корзина
# -------------------

def send_form_email(request) -> HttpResponse:
    product: Dict[str, Any] = request.session.get('stock_data')

    if request.method == "POST":
        quantity: int = int(request.POST.get('quantity', 1))
        unit_price: int = product['price']
        # Собираем информацию о пользователе
        user_data: Dict[str, str] = {
            'location': request.POST.get('location', '').strip(),
            'name': request.POST.get('name', '').strip(),
            'phone': request.POST.get('phone', '').strip(),
            'email': request.POST.get('email', '').strip(),
        }

        # Расчет стоимости
        items_price = unit_price * quantity

        # # Возвращаем JSON-ответ для обновления на странице
        subject: str = "Новый заказ"
        message: str = f"Заказ на товар: {product['name']}\n" \
                  f"Количество: {quantity}\n" \
                  f"Цена за единицу: {unit_price}\n" \
                  f"Итого: {items_price}\n" \
                  f"Данные покупателя:\n" \
                  f"Имя: {user_data['name']}\n" \
                  f"Телефон: {user_data['phone']}\n" \
                  f"Email: {user_data['email']}\n" \
                  f"Местоположение: {user_data['location']}"

        # Получаем email из данных формы (если нужно)
        recipient_list: List[str] = [EMAIL_HOST_USER]

        response_status: bool = False
        # Отправляем письмо в блоке try/except
        try:
            send_mail(subject, message, EMAIL_HOST_USER, recipient_list)
            response_status = True
        except Exception('Произошла ошибка отправки пиьсма. Обратитесь в поддержку') as e:
            exception_text: str = e

        request.session['response_status'] = response_status
        context: Dict[str, bool] = {
            "response_status": response_status
        }

        # Вернем сообщение об успешной отправке
        return render(request, 'success.html', context)


def get_order(request) -> HttpResponse:
    # Получаем данные товара из сессии
    product: Dict[str, Any] = request.session.get('stock_data')

    color = [prop['value'] for prop in product['properties'] if prop['name'] == 'Цвет'][0]

    context: Dict[str, Any] = {
        "product": product,
        "color": color,
        "memory": None,
        "quantity": 1,
        "items_price": product['price'],
    }
    if product['product_type'] == 'headphones' or product['product_type'] == 'accessories':
        context['memory'] = ''
    else:
        memory_size = [prop['value'] for prop in product['properties'] if prop['name'] == 'Встроенная память'][0]
        context['memory'] = memory_size

    return render(request, 'post.html', context)


def public_offer(request) -> HttpResponse:
    return render(request, 'public_offer.html')


def confidential_policy(request) -> HttpResponse:
    return render(request, 'confidential_policy.html')


def get_payment_details(request) -> HttpResponse:
    return render(request, 'payment_details.html')


#Функция получения/создания корзины пользователя
def get_user_cart(request: HttpRequest) -> Cart:
    """
    Получает (или создаёт) корзину текущего пользователя.

    Если пользователь авторизован, корзина привязывается к нему.
    Если нет — корзина привязывается к session_id (идентификатору сессии).

    :param request: HttpRequest объект, содержащий данные запроса.
    :return: Объект корзины (Cart).
    """
    if request.user.is_authenticated:
        # get_or_create возвращает кортеж из двух значений (объект корзины, True - если корзина создана, False - корзина уже существовала)
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        # Получаем session_id для анонимного пользователя
        session_id: Optional[str] = request.session.session_key
        # Если session_id отсутствует, создаём новую сессию
        if not session_id:
            request.session.create()
            session_id = request.session.session_key

        # Создаём или получаем корзину по session_id
        cart, created = Cart.objects.get_or_create(session_id=session_id)

    return cart


#Функция добавления товара в корзину
def add_to_cart(request: HttpRequest, stock_id: int) -> HttpResponseRedirect:
    cart: Cart = get_user_cart(request)
    stock_product: Stock = get_object_or_404(Stock, id=stock_id)
    cart_item: CartItem
    created: bool
    cart_item, created = CartItem.objects.get_or_create(cart=cart, stock_product=stock_product)
    # Если товар уже был в корзине, то есть ничего не создалось
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect("view_cart")

def remove_item_from_cart(request: HttpRequest, item_id: int) -> HttpResponseRedirect:
    """
    Функция удаления одной штуки из позиции товара из корзины
    Пример: Было 10 станет 9
    """
    cart_item: CartItem = get_object_or_404(CartItem, id = item_id)

    if cart_item.quantity <= 1:
        cart_item.delete()

    else:
        cart_item.quantity -= 1
        cart_item.save()

    return redirect("view_cart")


def remove_position_from_cart(request: HttpRequest, item_id: int) -> HttpResponseRedirect:
    """
    Функция удаления целой позиции товара из корзины
    Пример: Было 10 станет 0
    """
    cart_item: CartItem = get_object_or_404(CartItem, id = item_id)

    cart_item.delete()

    return redirect("view_cart")


#Функция отображения корзины пользователя
def view_cart(request: HttpRequest) -> HttpResponse:
    cart: Cart = get_user_cart(request)
    cart_items: QuerySet[CartItem] = CartItem.objects.filter(cart=cart)
    cart_total_price = sum(item.get_total_price for item in cart_items)
    context: Dict[str, Any] = {
        "cart_items": cart_items,
        "total_price": cart_total_price
    }

    return render(request, "cart.html", context)


# -------------------
# Оплата
# -------------------

# # Функция для создания платежа в Альфа-Кассе
# def create_payment(request: HttpRequest) -> HttpResponse:
#     """
#        Создаёт платёж в Альфа-Кассе.
#
#        1. Получает корзину пользователя и товары из неё.
#        2. Проверяет, пуста ли корзина.
#        3. Считает общую сумму заказа.
#        4. Генерирует уникальный order_id.
#        5. Формирует payload (данные для API Альфа-Кассы).
#        6. Отправляет POST-запрос в Альфа-Кассу.
#        7. Если успешно, перенаправляет пользователя на страницу оплаты.
#        8. Если ошибка — возвращает JSON с ошибкой.
#
#        :param request: HttpRequest — объект запроса от пользователя.
#        :return: HttpResponse — редирект на страницу оплаты или JSON с ошибкой.
#        """
#     # 1. Получаем корзину текущего пользователя
#     cart: Cart = get_user_cart(request)
#     cart_items: QuerySet[CartItem] = CartItem.objects.filter(cart=cart)
#     # 2. Проверяем, есть ли товары в корзине
#     if not cart_items.exists():
#         return JsonResponse({"error": "Корзина пустая"}, status = 400)
#     # 3. Считаем общую сумму заказа
#     total_price: int = sum(item.total_price for item in cart_items)
#     # 4. Генерируем уникальный ID заказа, переводим в str для отправить в API
#     order_id: str = str(uuid.uuid4())
#     # 5. Формируем payload для запроса в Альфа-Кассу
#     payload: dict[str, Any] = {
#         #Todo: добавить инфу про ALFA_параметры
#         "userName": settings.ALFA_MERCHANT_ID,
#         "password": settings.ALFA_SECRET,
#         "orderNumber": order_id,
#         "amount": total_price,
#         "currency": 643, # Российский рубль
#         #Todo: сделать html success_pay
#         "returnUrl": "https://iphoneondon.ru/success_pay/",
#         # Todo: сделать html payment_failed
#         "failUrl": "https://iphoneondon.ru/payment_failed/",
#         "description": f"Оплата заказа {order_id}",
#         "jsonParams": {"cart_id": cart.id},
#     }
#     # 6. Отправляем POST-запрос в API Альфа-Кассы
#     # Todo:Добавить ALFA_API_URL
#     response: request.Response = requests.post(settings.ALFA_API_URL + "register.do", data=payload)
#     # 7. Обрабатываем ответ от Альфа-Кассы
#     if response.status_code == 200 and response.json().get("orderId"):
#     #Если API вернул orderId — перенаправляем пользователя на страницу оплаты
#         return redirect(response.json()["formUrl"])
#     else:
#         # Если произошла ошибка — возвращаем JSON с деталями
#         return JsonResponse(
#             {
#                 "error": "Ошибка при создании платежа",
#                 "details": response.json()  # API обычно возвращает текст ошибки
#             },
#             status=400
#         )
#
# #Функция обрабатывает уведомление об оплате от Альфа-Кассы.
# @csrf_exempt  # Отключаем проверку CSRF для входящих запросов от Альфа-Кассы
# def alfa_callback(request: HttpRequest) -> JsonResponse:
#     """
#         Обрабатывает уведомление об оплате от Альфа-Кассы.
#
#         1. Проверяет, что запрос типа POST.
#         2. Достаёт `cart_id` и `orderStatus` из тела запроса.
#         3. Если `orderStatus == "1"` (оплата прошла успешно):
#             - Создаёт объект `Order` (Заказ).
#             - Удаляет все товары из корзины.
#         4. Возвращает JSON-ответ об успешной обработке.
#
#         :param request: HttpRequest — входящий HTTP-запрос.
#         :return: JsonResponse — JSON-ответ с результатом обработки.
#         """
#     # 1. Проверяем, что запрос типа POST
#     if request.method != "POST":
#         return JsonResponse({"error": "Метод не поддерживается"}, status=405)
#     try:
#         # 2. Парсим входные данные
#         data: dict = json.loads(request.body) # Альфа-Касса передаёт JSON-тело
#         cart_id: str | None = data.get("jsonParams", {}).get("cart_id") # Достаём cart_id
#         order_status: str | None = data.get("orderStatus")  # Достаём статус оплаты
#         if not cart_id or order_status is None:
#             return JsonResponse({"error": "Некорректные данные"}, status=400)
#         # 3. Если заказ успешно оплачен (`orderStatus == "1"`)
#         if order_status == '1':
#             cart: Cart = get_object_or_404(Cart, id=cart_id)
#             cart_items: QuerySet[CartItem] = CartItem.objects.filter(cart=cart)
#             # 4. Создаём заказ
#             total_price: int = sum(item.total_price for item in cart_items)
#             Order.objects.create(user=cart.user, total_price=total_price)
#             # 5. Очищаем корзину после успешной оплаты
#             cart_items.delete()
#         return JsonResponse({"status": "ok"})  # Отвечаем Альфа-Кассе, что запрос обработан
#     except json.JSONDecodeError:
#         return JsonResponse({"error": "Ошибка обработки JSON"}, status=400)
#     except Cart.DoesNotExist:
#         return JsonResponse({"error": "Корзина не найдена"}, status=404)


