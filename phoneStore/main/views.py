import json
from django.http import JsonResponse
from django.http import Http404
from typing import List, Any, Dict
from django.db.models import QuerySet
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView

from .models import ProductInstance, ProductType, PropertyType, PropertyInstance, ImagesInstance, Stock


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


def phones_catalog_two(request, product_type, product_name=None):
    # Базовый фильтр по типу продукта
    product_instances = ProductInstance.objects.filter(
        product_type_id__name=product_type
    )

    # Если задано имя продукта (slug), фильтруем дополнительно по нему
    if product_name:
        product_instances = product_instances.filter(slug=product_name)

    # Получаем только те товары, которые есть в наличии
    stocks = Stock.objects.filter(
        product_instance__in=product_instances,  # Привязываем Stock к выбранным ProductInstance
        quantity__gt=0  # Учитываем только товары в наличии
    ).prefetch_related(
        'product_instance',  # Подтягиваем данные о продукте
        'property_instances__property_type_id'  # Подтягиваем свойства и их типы
    )

    # Собираем изображения для продуктов
    image_instances = ImagesInstance.objects.filter(
        image_instance_id__in=product_instances
    )

    # Формируем контекст для шаблона
    context = {
        'product_instances': stocks,  # Товары с их количеством и параметрами
        'image_instances': image_instances,  # Картинки продуктов
    }

    return render(request, 'catalog.html', context)


# -----------
# Корзина
# -----------

def add_to_cart(request, product_id):
    """
    Добавление товара в корзину:
    """
    product = get_object_or_404(ProductInstance, id=product_id)
    quantity = int(request.GET.get('quantity', 1))  # Количество товара (по умолчанию 1)

    # Загружаем корзину из cookies
    cart = request.cart['cart']

    # Проверяем, есть ли товар уже в корзине
    for item in cart:
        if item['product_id'] == product_id:
            item['quantity'] += quantity
            break
    else:
        cart.append({'product_id': product_id, 'quantity': quantity})

    # Обновляем cookies
    response = JsonResponse({'message': 'Товар добавлен в корзину'})
    response.set_cookie('cart', json.dumps({'cart': cart}), httponly=True)

    return response


def remove_from_cart(request, product_id):
    """
    Удаление товара из корзины
    """
    cart = request.cart['cart']
    cart = [item for item in cart if item['product_id'] != product_id]

    response = JsonResponse({'message': 'Товар удалён из корзины'})
    response.set_cookie('cart', json.dumps({'cart': cart}), httponly=True)

    return response


def cart_detail(request):
    """
    Отображение корзины
    """
    cart = request.cart['cart']

    # Получаем товары из базы данных
    product_ids = [item['product_id'] for item in cart]
    products = ProductInstance.objects.filter(id__in=product_ids)

    # Собираем данные для отображения
    cart_items = []
    total_price = 0

    for item in cart:
        product = products.get(id=item['product_id'])
        price = product.propertyinstance_set.filter(property_type_id__name='Цена').first()
        price_value = int(price.value) if price else 0
        total_item_price = price_value * item['quantity']

        cart_items.append({
            'product': product,
            'quantity': item['quantity'],
            'price': price_value,
            'total_price': total_item_price,
        })

        total_price += total_item_price

    return render(request, 'cart_detail.html', {
        'cart_items': cart_items,
        'total_price': total_price,
    })
