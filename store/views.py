from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
import uuid
from .models import Product, Category, Cart, CartItem, Order, OrderItem


def product_list_view(request):
    products = Product.objects.filter(is_active=True).select_related('category')
    categories = Category.objects.filter(is_active=True)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    
    # Category filter
    category_slug = request.GET.get('category', '')
    if category_slug:
        products = products.filter(category__slug=category_slug)
    
    # Price filter
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # Sorting
    sort_by = request.GET.get('sort', 'name')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    elif sort_by == 'featured':
        products = products.order_by('-is_featured', 'name')
    else:
        products = products.order_by('name')
    
    # Pagination
    paginator = Paginator(products, 12)  # Show 12 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'search_query': search_query,
        'current_category': category_slug,
        'current_sort': sort_by,
        'min_price': min_price,
        'max_price': max_price,
    }
    return render(request, 'store/product_list.html', context)


def product_detail_view(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related_products = Product.objects.filter(
        category=product.category, 
        is_active=True
    ).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'store/product_detail.html', context)


def category_products_view(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = Product.objects.filter(category=category, is_active=True)
    
    # Apply same filtering and sorting as product_list_view
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    sort_by = request.GET.get('sort', 'name')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    else:
        products = products.order_by('name')
    
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
        'search_query': search_query,
        'current_sort': sort_by,
    }
    return render(request, 'store/category_products.html', context)


@require_POST
def add_to_cart_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Please log in to add items to cart'})
    
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = int(data.get('quantity', 1))
        
        product = get_object_or_404(Product, id=product_id, is_active=True)
        
        if quantity > product.stock:
            return JsonResponse({'success': False, 'message': 'Not enough stock available'})
        
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            if cart_item.quantity > product.stock:
                return JsonResponse({'success': False, 'message': 'Not enough stock available'})
            cart_item.save()
        
        return JsonResponse({
            'success': True,
            'message': f'{product.name} added to cart',
            'cart_items_count': cart.total_items,
            'cart_total': float(cart.total_price)
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': 'An error occurred'})


@login_required
def cart_view(request):
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.all().select_related('product')
    except Cart.DoesNotExist:
        cart_items = []
        cart = None
    
    context = {
        'cart_items': cart_items,
        'cart': cart,
    }
    return render(request, 'store/cart.html', context)


@login_required
@require_POST
def update_cart_item_view(request):
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        quantity = int(data.get('quantity'))
        
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        
        if quantity <= 0:
            cart_item.delete()
            message = 'Item removed from cart'
        else:
            if quantity > cart_item.product.stock:
                return JsonResponse({'success': False, 'message': 'Not enough stock available'})
            cart_item.quantity = quantity
            cart_item.save()
            message = 'Cart updated'
        
        cart = cart_item.cart if quantity > 0 else Cart.objects.get(user=request.user)
        
        return JsonResponse({
            'success': True,
            'message': message,
            'cart_items_count': cart.total_items,
            'cart_total': float(cart.total_price),
            'item_total': float(cart_item.total_price) if quantity > 0 else 0
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': 'An error occurred'})


@login_required
@require_POST
def remove_from_cart_view(request):
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')

        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        cart_item.delete()

        cart = Cart.objects.get(user=request.user)

        return JsonResponse({
            'success': True,
            'message': 'Item removed from cart',
            'cart_items_count': cart.total_items,
            'cart_total': float(cart.total_price)
        })

    except Exception as e:
        return JsonResponse({'success': False, 'message': 'An error occurred'})


@login_required
def checkout_view(request):
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.all().select_related('product')

        if not cart_items:
            messages.warning(request, 'Your cart is empty.')
            return redirect('store:cart')

        # Check stock availability
        for item in cart_items:
            if item.quantity > item.product.stock:
                messages.error(request, f'Not enough stock for {item.product.name}')
                return redirect('store:cart')

    except Cart.DoesNotExist:
        messages.warning(request, 'Your cart is empty.')
        return redirect('store:cart')

    if request.method == 'POST':
        # Create order
        order = Order.objects.create(
            user=request.user,
            order_number=f"ORD-{uuid.uuid4().hex[:8].upper()}",
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone'),
            address_line_1=request.POST.get('address_line_1'),
            address_line_2=request.POST.get('address_line_2', ''),
            city=request.POST.get('city'),
            state=request.POST.get('state'),
            postal_code=request.POST.get('postal_code'),
            country=request.POST.get('country'),
            total_amount=cart.total_price
        )

        # Create order items and update stock
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
            # Update product stock
            item.product.stock -= item.quantity
            item.product.save()

        # Clear cart
        cart.items.all().delete()

        messages.success(request, f'Order {order.order_number} placed successfully!')
        return redirect('store:order_confirmation', order_number=order.order_number)

    context = {
        'cart_items': cart_items,
        'cart': cart,
    }
    return render(request, 'store/checkout.html', context)


@login_required
def order_confirmation_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    context = {
        'order': order,
    }
    return render(request, 'store/order_confirmation.html', context)


@login_required
def order_detail_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    context = {
        'order': order,
    }
    return render(request, 'store/order_detail.html', context)
