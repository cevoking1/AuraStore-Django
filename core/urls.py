from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from shop.views import index, product_detail # Добавили product_detail
from shop.views import index, product_detail, add_to_cart, cart_detail, cart_clear # Добавь импорты
from shop.views import index, product_detail, add_to_cart, cart_detail, cart_clear, checkout, user_login, user_register, user_logout

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('product/<int:pk>/', product_detail, name='product_detail'),
    path('cart/', cart_detail, name='cart_detail'), # Страница корзины
    path('add-to-cart/<int:pk>/', add_to_cart, name='add_to_cart'), # Ссылка-действие
    path('cart-clear/', cart_clear, name='cart_clear'), # Очистка
    path('login/', user_login, name='login'),
    path('register/', user_register, name='register'),
    path('logout/', user_logout, name='logout'),
    path('checkout/', checkout, name='checkout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)