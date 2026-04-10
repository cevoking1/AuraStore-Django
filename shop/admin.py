from django.contrib import admin
from .models import Product, Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Колонки, которые будут видны в списке заказов
    list_display = ('id', 'first_name', 'phone', 'total_price', 'created_at', 'is_completed')
    # Фильтры справа
    list_filter = ('is_completed', 'created_at')
    # Возможность быстро поменять статус "Выполнен"
    list_editable = ('is_completed',)
    # Поиск по имени или телефону
    search_fields = ('first_name', 'phone')