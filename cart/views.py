from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from .models import Product, Cart, CartItem
from django.contrib import messages
from django.contrib.auth.decorators import login_required



@login_required(login_url='account:signin')
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    quantity = int(request.POST.get('quantity', 1))  # Default quantity is 1
    payment_type = request.POST.get('payment_type', 'installment')  # Default to installment if not specified

    track_installment_plan = ""
    installment_type = ''

    # Only process installment details if payment type is installment
    if payment_type == 'installment':
        # if installment plan is selected from Options (static plan) otherwise get dyanamic installment from session 
        static_installment_plan = request.POST.get('installment_plan')
        dynamic_installment_plan = request.session.get("installment_plan")

        if static_installment_plan:
            track_installment_plan = static_installment_plan
            installment_type = 'static'
        elif dynamic_installment_plan:
            track_installment_plan = str(dynamic_installment_plan)+"_months"
            installment_type = 'dynamic'
        else:
            # If no installment plan is selected but payment type is installment, show error
            messages.error(request, "Please select an installment plan.")
            return redirect('products:product_detail', product_id=product_id)

    # Get or create a cart for the current user
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Check if a cart item already exists
    existing_cart_item = CartItem.objects.filter(cart=cart).first()

    if existing_cart_item:
        # If the cart item already exists, delete it
        existing_cart_item.delete()

    # Create a new cart item with the updated details
    new_cart_item = CartItem(
        cart=cart, 
        product=product, 
        quantity=quantity, 
        installment_plan=track_installment_plan, 
        installment_type=installment_type,
        payment_type=payment_type
    )
    new_cart_item.save()    

    messages.success(request, "Product added to cart.")
    
    return redirect('cart:view')
 


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
    return redirect('cart:view') 


def clear_all_cart(request):
    cart = get_object_or_404(Cart, user=request.user)
    
    # Get the CartItem to remove
    cart_items = CartItem.objects.filter(cart=cart)
    
    # Remove the items from the cart
    cart_items.delete()
    return redirect('cart:view')
    
    
