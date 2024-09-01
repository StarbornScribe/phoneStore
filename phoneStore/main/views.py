from django.shortcuts import render

# Create your views here.


def bootstrap_page_handler(request):
    return render(request, 'index.html')


def view_single_product(request):
    return render(request, 'single-product.html')


# def home_page_view(request):
#     product_instances: QuerySet = ProductInstance.objects.all()
#     properties: List = [product_instance.name for product_instance in product_instances]
#     print(product_instances)
#
#     context = {
#         'product_instances': product_instances,
#         'properties': properties
#     }
#
#     return render(request, '.html', context)