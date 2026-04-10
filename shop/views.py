from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import Product, Order, Category, ProductVariant, OrderItem

# --- ГЛАВНЫЕ СТРАНИЦЫ ---

def index(request):
    products = Product.objects.filter(is_active=True)
    
    # Логика поиска
    query = request.GET.get('q')
    if query:
        products = products.filter(name__icontains=query)
    
    # Логика сортировки
    sort = request.GET.get('sort')
    if sort == 'price_asc':
        products = products.order_by('base_price')
    elif sort == 'price_desc':
        products = products.order_by('-base_price')
    elif sort == 'newest':
        products = products.order_by('-created_at')
        
    return render(request, 'shop/index.html', {
        'products': products, 
        'query': query, 
        'sort': sort
    })

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.products.filter(is_active=True)
    
    # Сортировка внутри категории
    sort = request.GET.get('sort')
    if sort == 'price_asc':
        products = products.order_by('base_price')
    elif sort == 'price_desc':
        products = products.order_by('-base_price')
        
    return render(request, 'shop/category_detail.html', {
        'category': category, 
        'products': products, 
        'sort': sort
    })

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'shop/detail.html', {'product': product})

# --- КОРЗИНА С УЧЕТОМ СКЛАДА ---

def add_to_cart(request, pk):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        variant_id = request.POST.get('variant_id', '0') 
        item_key = f"{pk}-{variant_id}"
        
        try:
            if variant_id != '0':
                obj = ProductVariant.objects.get(id=variant_id)
            else:
                obj = Product.objects.get(pk=pk)
            
            current_in_cart = cart.get(item_key, 0)
            if obj.stock > current_in_cart:
                cart[item_key] = current_in_cart + 1
                messages.success(request, "Товар добавлен в корзину")
            else:
                messages.error(request, "К сожалению, товар закончился на складе")
        except (Product.DoesNotExist, ProductVariant.DoesNotExist):
            messages.error(request, "Товар не найден")
        
        request.session['cart'] = cart
    return redirect('cart_detail')

def cart_detail(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0
    keys_to_remove = []

    for item_key, quantity in cart.items():
        try:
            product_id, variant_id = item_key.split('-')
            product = Product.objects.get(pk=product_id)
            variant = None
            price = product.base_price
            image_url = product.image.url if product.image else ''
            stock = product.stock
            
            if variant_id != '0':
                variant = ProductVariant.objects.get(id=variant_id)
                price = variant.price
                stock = variant.stock
                if variant.variant_image:
                    image_url = variant.variant_image.url
            
            if quantity > stock:
                quantity = stock
                cart[item_key] = quantity
            
            if quantity <= 0:
                keys_to_remove.append(item_key)
                continue

            item_total = price * quantity
            total_price += item_total
            
            cart_items.append({
                'item_key': item_key, 'product': product, 'variant': variant,
                'quantity': quantity, 'price': price, 'item_total': item_total, 
                'image_url': image_url, 'stock': stock
            })
        except:
            keys_to_remove.append(item_key)

    if keys_to_remove:
        for key in keys_to_remove:
            cart.pop(key, None)
        request.session['cart'] = cart
        
    return render(request, 'shop/cart.html', {'cart_items': cart_items, 'total_price': total_price})

def cart_update(request, item_key, action):
    cart = request.session.get('cart', {})
    if item_key in cart:
        try:
            product_id, variant_id = item_key.split('-')
            if variant_id != '0':
                stock = ProductVariant.objects.get(id=variant_id).stock
            else:
                stock = Product.objects.get(pk=product_id).stock

            if action == 'plus':
                if cart[item_key] < stock:
                    cart[item_key] += 1
                else:
                    messages.warning(request, "Больше нет в наличии")
            elif action == 'minus':
                cart[item_key] -= 1
                if cart[item_key] <= 0:
                    del cart[item_key]
            
            request.session['cart'] = cart
        except:
            pass
    return redirect('cart_detail')

def cart_remove(request, item_key):
    cart = request.session.get('cart', {})
    if item_key in cart:
        del cart[item_key]
        request.session['cart'] = cart
        messages.info(request, "Товар удален из корзины")
    return redirect('cart_detail')

def cart_clear(request):
    if 'cart' in request.session:
        del request.session['cart']
        messages.info(request, "Корзина очищена")
    return redirect('index')

# --- ОФОРМЛЕНИЕ ЗАКАЗА СО СПИСАНИЕМ СО СКЛАДА ---

@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('index')
    
    total_price = 0
    items_to_create = []
    
    for item_key, qty in cart.items():
        try:
            p_id, v_id = item_key.split('-')
            product = Product.objects.get(pk=p_id)
            variant = ProductVariant.objects.get(id=v_id) if v_id != '0' else None
            price = variant.price if variant else product.base_price
            stock = variant.stock if variant else product.stock
            
            if stock < qty:
                messages.error(request, f"К сожалению, {product.name} недостаточно на складе.")
                return redirect('cart_detail')
                
            total_price += price * qty
            items_to_create.append({
                'product': product, 'variant': variant, 'price': price, 'qty': qty
            })
        except:
            return redirect('cart_detail')
    
    if request.method == 'POST':
        with transaction.atomic():
            order = Order.objects.create(
                user=request.user, 
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name'),
                phone=request.POST.get('phone'),
                address=request.POST.get('address'),
                total_price=total_price
            )
            
            for item in items_to_create:
                OrderItem.objects.create(
                    order=order, product=item['product'], variant=item['variant'],
                    price=item['price'], quantity=item['qty']
                )
                
                if item['variant']:
                    item['variant'].stock -= item['qty']
                    item['variant'].save()
                else:
                    item['product'].stock -= item['qty']
                    item['product'].save()
            
            del request.session['cart']
            messages.success(request, f"Заказ №{order.id} успешно оформлен!")
            return render(request, 'shop/success.html', {'order': order})
        
    return render(request, 'shop/checkout.html', {'total_price': total_price})

# --- ПОЛЬЗОВАТЕЛЬСКИЕ ФУНКЦИИ ---

@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'shop/profile.html', {'orders': orders})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"С возвращением, {user.username}!")
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
            messages.success(request, "Аккаунт успешно создан. Добро пожаловать!")
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'shop/register.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.info(request, "Вы вышли из системы.")
    return redirect('index')