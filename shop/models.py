from django.db import models
from django.contrib.auth.models import User

# --- КАТЕГОРИИ ДЛЯ МАГАЗИНА ---
class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название категории")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="URL-адрес (slug)")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name

# --- СПРАВОЧНИКИ ПАРАМЕТРОВ ---
class Color(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название цвета")
    
    class Meta:
        verbose_name = "Цвет"
        verbose_name_plural = "Цвета"
        
    def __str__(self):
        return self.name

class Memory(models.Model):
    size = models.CharField(max_length=50, verbose_name="Объем памяти")
    
    class Meta:
        verbose_name = "Объем памяти"
        verbose_name_plural = "Варианты памяти"
        
    def __str__(self):
        return self.size

# --- ОСНОВНАЯ ТАБЛИЦА ТОВАРОВ ---
class Product(models.Model):
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name='products', 
        verbose_name="Категория", 
        null=True, 
        blank=True
    )
    name = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    base_price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="Базовая цена (₸)")
    
    # Главное фото (отображается в каталоге)
    image = models.ImageField(upload_to='products/', verbose_name="Главное фото (общее)")
    image_2 = models.ImageField(upload_to='products/', verbose_name="Фото 2", null=True, blank=True)
    image_3 = models.ImageField(upload_to='products/', verbose_name="Фото 3", null=True, blank=True)
    
    # Характеристики в формате Ключ: Значение
    specs = models.TextField(
        verbose_name="Характеристики", 
        help_text="Формат: Название: Значение (каждое с новой строки)", 
        null=True, 
        blank=True
    )
    
    is_active = models.BooleanField(default=True, verbose_name="В продаже")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления", null=True)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['-created_at']

    def get_specs_list(self):
        """Парсит текстовое поле характеристик для шаблона"""
        if not self.specs:
            return []
        lines = self.specs.strip().split('\n')
        return [line.split(':', 1) for line in lines if ':' in line]

    def __str__(self):
        return self.name

# --- ВАРИАНТЫ ТОВАРА (ЦЕНА И ФОТО ЗАВИСЯТ ОТ ЭТОГО) ---
class ProductVariant(models.Model):
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='variants', 
        verbose_name="Товар"
    )
    color = models.ForeignKey(Color, on_delete=models.CASCADE, verbose_name="Цвет")
    memory = models.ForeignKey(Memory, on_delete=models.CASCADE, verbose_name="Память")
    price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="Цена для этой версии (₸)")
    variant_image = models.ImageField(
        upload_to='products/variants/', 
        verbose_name="Фото этого цвета", 
        null=True, 
        blank=True
    )

    class Meta:
        verbose_name = "Вариант товара"
        verbose_name_plural = "Варианты (Цены и Фото)"

    def __str__(self):
        return f"{self.product.name} - {self.color.name} - {self.memory.size}"

# --- ТАБЛИЦА ЗАКАЗОВ ---
class Order(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='orders', 
        verbose_name="Пользователь", 
        null=True, 
        blank=True
    )
    first_name = models.CharField(max_length=50, verbose_name="Имя")
    last_name = models.CharField(max_length=50, verbose_name="Фамилия")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    address = models.CharField(max_length=250, verbose_name="Адрес доставки")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата заказа")
    total_price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="Сумма (₸)")
    is_completed = models.BooleanField(default=False, verbose_name="Выполнен")

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created_at']

    def __str__(self):
        return f"Заказ №{self.id} — {self.first_name}"