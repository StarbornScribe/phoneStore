(function($) {
    $(document).ready(function() {
        var $productField = $('#id_product_instance');
        var $propertiesField = $('#id_properties');

        $productField.change(function() {
            var productId = $(this).val();
            if (!productId) {
                $propertiesField.empty();
                return;
            }

            // Запрос для получения свойств по product_instance
            $.ajax({
                url: `/api/properties/${productId}/`,  // Создайте API-эндпоинт для фильтрации
                success: function(data) {
                    $propertiesField.empty();
                    data.forEach(function(item) {
                        $propertiesField.append(
                            $('<option></option>').val(item.id).text(item.name)
                        );
                    });
                }
            });
        });
    });
})(django.jQuery);
