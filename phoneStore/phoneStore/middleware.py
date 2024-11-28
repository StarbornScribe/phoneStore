import json

class CartMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Загружаем корзину из cookies
        cart_data = request.COOKIES.get('cart', '{"cart": []}')
        try:
            request.cart = json.loads(cart_data)
        except json.JSONDecodeError:
            request.cart = {"cart": []}
        response = self.get_response(request)
        return response
