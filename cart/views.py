from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from .models import Product, Cart, CartItem
from django.contrib import messages
from django.contrib.auth.decorators import login_required



@login_required(login_url='account:signin')
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    quantity = int(request.POST.get('quantity', 1))
    installment_plan = request.POST.get('installment_plan')

    # Validate that an installment plan was selected
    if not installment_plan:
        messages.error(request, "Please select an installment plan.")
        return redirect('cart:cart')  

    # Get or create a cart for the current user
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Get or create a cart item for the specified product
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product, installment_plan=installment_plan)

    if not item_created:
        # cart_item.quantity += quantity
        cart_item.delete()
    else:
        cart_item.quantity = quantity
    
    # Save the selected installment plan in the cart item
    cart_item.save()

    return redirect('cart:cart') 


@login_required(login_url='account:signin')
def cart_page(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()
    total = cart.total_price()
    
    # Check if the cart is empty
    cart_is_empty = cart_items.count() == 0
    return render(request, 'cart/cart.html', {'cart_items': cart_items, 'total': total, 'cart_is_empty':cart_is_empty})



@login_required(login_url='account:signin')
def clear_cart(request, product_id):
    cart = get_object_or_404(Cart, user=request.user)
    
    # Get the CartItem to remove
    cart_item = get_object_or_404(CartItem, product=product_id, cart=cart)
    
    # Remove the item from the cart
    cart_item.delete()
    return redirect('cart:cart') 


# def total_cart_items(request):
#     if request.user.is_authenticated:
#         cart, created = Cart.objects.get_or_create(user=request.user)
#         cart_item_count = cart.items.count()
#     else:
#         cart_item_count = 0  

#     return render(request, 'base/navbar.html', {'cart_item_count': cart_item_count})
    
    
