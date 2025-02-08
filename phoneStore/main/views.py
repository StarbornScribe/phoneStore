from typing import List, Any, Dict
from django.views.generic import DetailView
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.core.mail import send_mail
from phoneStore.settings import EMAIL_HOST_USER
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

    # def get_object(self, queryset=None):
    #     # Fetch the object based on the slug
    #     slug = self.kwargs.get('slug')
    #
    #     return PropertyInstance

  
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


# -----------
# Корзина
# -----------

# def add_to_cart(request, product_id):
#     """
#     Добавление товара в корзину:
#     """
#     product = get_object_or_404(ProductInstance, id=product_id)
#     quantity = int(request.GET.get('quantity', 1))  # Количество товара (по умолчанию 1)
#
#     # Загружаем корзину из cookies
#     cart = request.cart['cart']
#
#     # Проверяем, есть ли товар уже в корзине
#     for item in cart:
#         if item['product_id'] == product_id:
#             item['quantity'] += quantity
#             break
#     else:
#         cart.append({'product_id': product_id, 'quantity': quantity})
#
#     # Обновляем cookies
#     response = JsonResponse({'message': 'Товар добавлен в корзину'})
#     response.set_cookie('cart', json.dumps({'cart': cart}), httponly=True)
#
#     return response


# def remove_from_cart(request, product_id):
#     """
#     Удаление товара из корзины
#     """
#     cart = request.cart['cart']
#     cart = [item for item in cart if item['product_id'] != product_id]
#
#     response = JsonResponse({'message': 'Товар удалён из корзины'})
#     response.set_cookie('cart', json.dumps({'cart': cart}), httponly=True)
#
#     return response


# def cart_detail(request):
#     """
#     Отображение корзины
#     """
#     cart = request.cart['cart']
#
#     # Получаем товары из базы данных
#     product_ids = [item['product_id'] for item in cart]
#     products = ProductInstance.objects.filter(id__in=product_ids)
#
#     # Собираем данные для отображения
#     cart_items = []
#     total_price = 0
#
#     for item in cart:
#         product = products.get(id=item['product_id'])
#         price = product.propertyinstance_set.filter(property_type_id__name='Цена').first()
#         price_value = int(price.value) if price else 0
#         total_item_price = price_value * item['quantity']
#
#         cart_items.append({
#             'product': product,
#             'quantity': item['quantity'],
#             'price': price_value,
#             'total_price': total_item_price,
#         })
#
#         total_price += total_item_price
#
#     return render(request, 'cart_detail.html', {
#         'cart_items': cart_items,
#         'total_price': total_price,
#     })



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

