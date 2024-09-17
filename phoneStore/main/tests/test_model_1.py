from django.test import TestCase
from main.models import ProductType

class TestProductType(TestCase):
    def setUp(self):
        self.product_type_phone = ProductType.objects.create(name='phone')
        self.product_type_watches = ProductType.objects.create(name='watches')
    def test_product_type_creation(self):
        self.assertEqual(self.product_type_phone.name, 'phone')
        self.assertTrue(isinstance(self.product_type_phone, ProductType))
        self.assertEqual(self.product_type_watches.name, 'watches')
        self.assertTrue(isinstance(self.product_type_watches, ProductType))

    def test_product_type_str(self):
        self.assertEqual(str(self.product_type_phone), 'phone')
        self.assertEqual(str(self.product_type_watches), 'watches')



