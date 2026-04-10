from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Product, Order

# --- НАСТРОЙКА ТОВАРОВ ---
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # Что отображаем в списке
    list_display = ('get_image', 'name', 'price', 'created_at')
    # По каким полям можно кликнуть, чтобы зайти в товар
    list_display_links = ('get_image', 'name')
    # Фильтры справа
    list_filter = ('created_at',)
    # Поиск по названию
    search_fields = ('name', 'description')
    # Редактирование цены прямо в списке
    list_editable = ('price',)
    # Поля, которые нельзя менять в самой карточке (только для просмотра)
    readonly_fields = ('get_image_big',)

    # Метод для миниатюры в списке (иконка товара)
    def get_image(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" style="object-fit:contain; border-radius:8px;">')
        return "Нет фото"
    get_image.short_description = "Фото"

    # Метод для большого превью внутри карточки товара
    def get_image_big(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="250" style="object-fit:contain; border-radius:15px;">')
        return "Нет фото"
    get_image_big.short_description = "Превью фото"


# --- НАСТРОЙКА ЗАКАЗОВ ---
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Основная инфо в списке заказов
    list_display = ('id', 'first_name', 'last_name', 'total_price', 'created_at', 'is_completed')
    # Фильтры для удобства менеджера
    list_filter = ('is_completed', 'created_at')
    # Ставим галочку "Выполнено" не заходя внутрь
    list_editable = ('is_completed',)
    # Поиск по всем контактным данным
    search_fields = ('first_name', 'last_name', 'phone', 'address')
    
    # Красивые блоки внутри заказа
    fieldsets = (
        ('Информация о клиенте', {
            'fields': ('user', 'first_name', 'last_name', 'phone', 'address')
        }),
        ('Финансы и статус', {
            'fields': ('total_price', 'is_completed', 'created_at')
        }),
    )
    # Эти поля нельзя менять вручную, так как их ставит система
    readonly_fields = ('created_at', 'total_price', 'user')

# --- КАСТОМИЗАЦИЯ ТЕКСТА АДМИНКИ ---
admin.site.site_header = "Aura Store | Управление магазином"
admin.site.site_title = "Aura Admin"
admin.site.index_title = "Консоль администратора Aura"