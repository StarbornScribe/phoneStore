from django.shortcuts import render
from .models import ProductInstance, ProductType, PropertyType, PropertyInstance, ImagesInstance
from typing import List
from django.db.models import QuerySet
# import logging
# logger = logging.getLogger(__name__)
# import pdb; pdb.set_trace()
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView
from django.http import Http404

# Create your views here.


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


class PhoneDetailView(DetailView):
    model = PropertyInstance
    template_name = 'single-product-slider.html'
    context_object_name = 'phone'

    def get_object(self, queryset=None):
        # Fetch the object based on the slug
        slug = self.kwargs.get('slug')
        return ProductInstance.objects.get(slug=slug)

  
def phones_catalog(request):
    # logger.info("View accessed")
    # pdb.set_trace()
    # This is a basic check to see if the view is reached.
    # Retrieve all product instances
    product_instances = ProductInstance.objects.filter(product_type_id__name='phones').prefetch_related(
        'propertyinstance_set__property_type_id')

    # product_instances: ProductInstance = ProductInstance.objects.all().prefetch_related('propertyinstance_set__property_type_id')
    image_instances: ImagesInstance = ImagesInstance.objects.all()

    # image_instances: ImagesInstance = ImagesInstance.objects.select_related('image_instance_id__product_type_id')
    context = {
        'product_instances': product_instances,
        'image_instances': image_instances,
    }

    return render(request, 'shop-left-sidebar.html', context)

  
def view_shop_catalog(request):
    return render(request, 'test.html')