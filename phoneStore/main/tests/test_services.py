from django.test import TestCase
from main.models import Order, OrderItem, ProductType, ProductInstance, PropertyType, PropertyInstance


class TestServices(TestCase):
    def setUp(self):
        product_type: ProductType = ProductType.objects.create(name='phones')
        product_instance: ProductInstance = ProductInstance.objects.create(
            product_type=product_type,
            name='iPhone 15',
            slug='iphone-15'
        )
        property_type_1: PropertyType = PropertyType.objects.create(
            product_type_id=product_type,
            name='Цвет'
        )
        property_type_2: PropertyType = PropertyType.objects.create(
            product_type_id=product_type,
            name='Встроенная память'
        )

        property_instance: PropertyInstance = PropertyInstance.objects.create(
            product_instance_id='',
            property_type_id='',
            value=''
        )

        Order.objects.create(
            user_id=None,
            customer_name="Test",
            customer_phone='+79999671010',
            customer_email='test@test.ru',
            customer_address='Test',
            is_delivery='',
            currency_code='',
            total_price='',
            payment_type='',
            status='',
            acquiring_order_id=''
        )

    def tearDown(self):
        pass

    def test_create_order_in_db(self):
        pass
