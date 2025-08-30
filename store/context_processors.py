from .models import Cart


def cart_context(request):
    """
    Context processor to make cart information available in all templates
    """
    cart_items_count = 0
    cart_total = 0
    
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_items_count = cart.total_items
            cart_total = cart.total_price
        except Cart.DoesNotExist:
            pass
    else:
        # For anonymous users, use session-based cart
        cart = request.session.get('cart', {})
        cart_items_count = sum(item['quantity'] for item in cart.values())
        # Calculate total from session cart if needed
    
    return {
        'cart_items_count': cart_items_count,
        'cart_total': cart_total,
    }
