from django.db import models
from django.contrib.auth.models import User

# --- ТАБЛИЦА ТОВАРОВ ---
class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="Цена (₸)")
    image = models.ImageField(upload_to='products/', verbose_name="Фото")
    is_active = models.BooleanField(default=True, verbose_name="В продаже")
    # Добавляем created_at, чтобы админка не ругалась
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления", null=True)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['-created_at']

    def __str__(self):
        return self.name


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