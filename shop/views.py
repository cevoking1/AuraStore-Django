from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Product, Order, Category # Добавлен импорт Category

# --- ГЛАВНАЯ СТРАНИЦА ---
def index(request):
    # Получаем все активные товары и все категории для навигации
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all()
    return render(request, 'shop/index.html', {
        'products': products,
        'categories': categories
    })

# --- СТРАНИЦА КАТЕГОРИИ (НОВОЕ) ---
def category_detail(request, slug):
    # Находим категорию по её slug (например, 'smartphones')
    category = get_object_or_404(Category, slug=slug)
    # Фильтруем товары только этой категории
    products = category.products.filter(is_active=True)
    return render(request, 'shop/category_detail.html', {
        'category': category,
        'products': products
    })

# --- ДЕТАЛИ ТОВАРА ---
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'shop/detail.html', {'product': product})

# --- КОРЗИНА ---
def add_to_cart(request, pk):
    cart = request.session.get('cart', {})
    pk_str = str(pk)
    cart[pk_str] = cart.get(pk_str, 0) + 1
    request.session['cart'] = cart
    return redirect('cart_detail')

def cart_detail(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0
    for pk, quantity in cart.items():
        product = get_object_or_404(Product, pk=pk)
        item_total = product.price * quantity
        total_price += item_total
        cart_items.append({'product': product, 'quantity': quantity, 'item_total': item_total})
    return render(request, 'shop/cart.html', {'cart_items': cart_items, 'total_price': total_price})

def cart_clear(request):
    if 'cart' in request.session:
        del request.session['cart']
    return redirect('index')

# --- ОФОРМЛЕНИЕ ЗАКАЗА ---
@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('index')
    
    if request.method == 'POST':
        total = 0
        for pk, qty in cart.items():
            product = Product.objects.get(pk=pk)
            total += product.price * qty
        
        order = Order.objects.create(
            user=request.user, 
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            phone=request.POST.get('phone'),
            address=request.POST.get('address'),
            total_price=total
        )
        del request.session['cart']
        return render(request, 'shop/success.html', {'order': order})
    return render(request, 'shop/checkout.html')

# --- ЛИЧНЫЙ КАБИНЕТ ---
@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'shop/profile.html', {'orders': orders})

# --- АВТОРИЗАЦИЯ ---
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'shop/login.html', {'form': form})

def user_register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'shop/register.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('index')