from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Product, Order, Color, Memory, Category, ProductVariant

# --- ИНЛАЙНЫ (Редактирование цен и фото вариантов внутри товара) ---
class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ('color', 'memory', 'price', 'variant_image', 'get_preview')
    readonly_fields = ('get_preview',)

    def get_preview(self, obj):
        if obj.variant_image:
            return mark_safe(f'<img src="{obj.variant_image.url}" width="50" height="50" style="object-fit:contain; border-radius:4px;">')
        return "-"
    get_preview.short_description = "Превью"

# --- НАСТРОЙКА КАТЕГОРИЙ ---
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)} # Авто-заполнение адреса из названия
    search_fields = ('name',)

# --- НАСТРОЙКА ТОВАРОВ ---
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # Что отображаем в списке
    list_display = ('get_image', 'name', 'category', 'base_price', 'is_active')
    list_display_links = ('get_image', 'name')
    list_editable = ('base_price', 'is_active', 'category')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    
    # Подключаем варианты (цены/цвета) прямо сюда
    inlines = [ProductVariantInline]
    
    # Группировка полей в карточке
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'category', 'description', 'base_price', 'is_active')
        }),
        ('Визуальный контент', {
            'fields': ('image', 'specs')
        }),
    )

    def get_image(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" style="object-fit:contain; border-radius:8px;">')
        return "Нет фото"
    get_image.short_description = "Фото"

# --- НАСТРОЙКА ЗАКАЗОВ ---
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'total_price', 'is_completed', 'created_at')
    list_filter = ('is_completed', 'created_at')
    list_editable = ('is_completed',)
    search_fields = ('first_name', 'last_name', 'phone')
    readonly_fields = ('created_at', 'total_price', 'user')

# --- СПРАВОЧНИКИ ---
@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Memory)
class MemoryAdmin(admin.ModelAdmin):
    list_display = ('size',)

# Кастомизация заголовков
admin.site.site_header = "Aura Store | Управление магазином"
admin.site.site_title = "Aura Admin"
admin.site.index_title = "Консоль администратора Aura"