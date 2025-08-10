"""
URL configuration for phoneStore project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from main import views
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from main.views import add_to_cart, view_cart, remove_item_from_cart, remove_position_from_cart


urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('', views.bootstrap_page_handler, name='home'),
    path('product/<slug:slug>/<int:stock_id>', views.product_detail_view, name='product-detail'),
    # path('phones-catalog/', views.phones_catalog, name='phones_catalog'),
    path('phones-catalog/<str:product_type>', views.phones_catalog_thrid, name='phones_catalog'),
    path('phones-catalog/<str:product_type>/<str:product_name>', views.phones_catalog_thrid, name='phones_catalog_with_name'),
    path('create', views.get_order, name='create_order'),
    path('success', views.send_form_email, name='send_form_email'),
    path("cart/", view_cart, name="view_cart"),
    path("cart/add/<int:stock_id>/", add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', remove_item_from_cart, name='remove_item_from_cart'),
    path('cart/remove_position/<int:item_id>/', remove_position_from_cart, name='remove_position_from_cart'),
    path('public_offer', views.public_offer, name='public_offer'),
    path('confidential_policy', views.confidential_policy, name='confidential_policy'),
    path('payment_details', views.get_payment_details, name='payment_details')
    # path("checkout/", create_payment, name="checkout"),
    # path("alfa-callback/", alfa_callback, name="alfa_callback"),
    # path('send_form', views.send_form_email, name='send_form'),
    # path('your-name/', views.get_name, name='your_name')
]

if settings.DEBUG:
    # urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # Serving media files (user uploads)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
