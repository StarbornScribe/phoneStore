from django.shortcuts import render

# Create your views here.


def bootstrap_page_handler(request):
    return render(request, 'index.html')


def view_single_product(request):
    return render(request, 'single-product.html')