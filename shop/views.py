from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Product, Order, Category, ProductVariant, OrderItem

def index(request):
    products = Product.objects.filter(is_active=True)
    return render(request, 'shop/index.html', {'products': products})

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.products.filter(is_active=True)
    return render(request, 'shop/category_detail.html', {'category': category, 'products': products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'shop/detail.html', {'product': product})

# --- ЛОГИКА КОРЗИНЫ (ОБНОВЛЕНА) ---
def add_to_cart(request, pk):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        # Получаем ID варианта из формы. Если вариантов нет, будет '0'
        variant_id = request.POST.get('variant_id', '0') 
        
        # Ключ в корзине теперь выглядит так: "IDтовара-IDварианта" (например, "3-12")
        item_key = f"{pk}-{variant_id}"
        cart[item_key] = cart.get(item_key, 0) + 1
        
        request.session['cart'] = cart
    return redirect('cart_detail')

def cart_detail(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0
    
    for item_key, quantity in cart.items():
        product_id, variant_id = item_key.split('-')
        product = get_object_or_404(Product, pk=product_id)
        
        variant = None
        price = product.base_price
        image_url = product.image.url if product.image else ''
        
        # Если у товара был выбран вариант
        if variant_id != '0':
            variant = ProductVariant.objects.get(id=variant_id)
            price = variant.price
            if variant.variant_image:
                image_url = variant.variant_image.url
                
        item_total = price * quantity
        total_price += item_total
        
        cart_items.append({
            'item_key': item_key,
            'product': product,
            'variant': variant,
            'quantity': quantity,
            'price': price,
            'item_total': item_total,
            'image_url': image_url
        })
        
    return render(request, 'shop/cart.html', {'cart_items': cart_items, 'total_price': total_price})

def cart_remove(request, item_key):
    # Получаем корзину
    cart = request.session.get('cart', {})
    
    # Если такой ключ (например, '3-12') есть в корзине — удаляем его
    if item_key in cart:
        del cart[item_key]
        request.session['cart'] = cart # Сохраняем обновленную корзину
        
    return redirect('cart_detail')

def cart_clear(request):
    if 'cart' in request.session:
        del request.session['cart']
    return redirect('index')

# --- ОФОРМЛЕНИЕ ЗАКАЗА (ОБНОВЛЕНО) ---
@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('index')
    
    # Считаем общую сумму перед загрузкой страницы или сохранением
    total_price = 0
    items_to_create = []
    
    for item_key, qty in cart.items():
        product_id, variant_id = item_key.split('-')
        product = Product.objects.get(pk=product_id)
        variant = ProductVariant.objects.get(id=variant_id) if variant_id != '0' else None
        price = variant.price if variant else product.base_price
        
        total_price += price * qty
        items_to_create.append({
            'product': product, 'variant': variant, 'price': price, 'quantity': qty
        })
    
    if request.method == 'POST':
        # Создаем сам заказ
        order = Order.objects.create(
            user=request.user, 
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            phone=request.POST.get('phone'),
            address=request.POST.get('address'),
            total_price=total_price
        )
        
        # Создаем записи о том, КАКИЕ ИМЕННО ТОВАРЫ лежат в заказе
        for item in items_to_create:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                variant=item['variant'],
                price=item['price'],
                quantity=item['quantity']
            )
            
        del request.session['cart']
        return render(request, 'shop/success.html', {'order': order})
        
    return render(request, 'shop/checkout.html', {'total_price': total_price})

# --- ОСТАЛЬНОЕ БЕЗ ИЗМЕНЕНИЙ ---
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