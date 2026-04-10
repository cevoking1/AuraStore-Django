from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Category, Color, Memory, Product, ProductVariant, Order, OrderItem

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    # ДОБАВИЛИ STOCK
    fields = ('color', 'memory', 'price', 'stock', 'variant_image', 'get_preview')
    readonly_fields = ('get_preview',)

    def get_preview(self, obj):
        if obj.variant_image:
            return mark_safe(f'<img src="{obj.variant_image.url}" width="50" height="50" style="object-fit:contain; border-radius:4px;">')
        return "-"
    get_preview.short_description = "Превью"

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product', 'variant']
    extra = 0
    readonly_fields = ['price']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)} 
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # ДОБАВИЛИ STOCK В СПИСОК
    list_display = ('get_image', 'name', 'category', 'base_price', 'stock', 'is_active')
    list_display_links = ('get_image', 'name')
    list_editable = ('base_price', 'stock', 'is_active', 'category')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    
    inlines = [ProductVariantInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'category', 'description', 'base_price', 'stock', 'is_active')
        }),
        ('Визуальный контент и характеристики', {
            'fields': ('image', 'image_2', 'image_3', 'specs')
        }),
    )

    def get_image(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" style="object-fit:contain; border-radius:8px;">')
        return "Нет фото"
    get_image.short_description = "Фото"

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'total_price', 'is_completed', 'created_at')
    list_filter = ('is_completed', 'created_at')
    list_editable = ('is_completed',)
    search_fields = ('first_name', 'last_name', 'phone')
    readonly_fields = ('created_at', 'total_price', 'user')
    inlines = [OrderItemInline] 

@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Memory)
class MemoryAdmin(admin.ModelAdmin):
    list_display = ('size',)

admin.site.site_header = "Aura Store | Управление магазином"
admin.site.site_title = "Aura Admin"
admin.site.index_title = "Консоль администратора Aura"