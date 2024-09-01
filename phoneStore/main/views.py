from django.shortcuts import render

# Create your views here.


def bootstrap_page_handler(request):
    return render(request, 'index.html')


def view_single_product(request):
    return render(request, 'single-product.html')


def view_shop_catalog(request):
    return render(request, 'single-catalog.html')