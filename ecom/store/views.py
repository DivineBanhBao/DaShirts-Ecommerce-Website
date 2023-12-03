from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import *
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP

def category(request,cate):
    #Grab category from url
    try:
        #look up category
        category = Category.objects.get(name=cate)
        products = Product.objects.filter(category=category)
        return render(request, 'category.html', {'products':products, 'category':category} )
    except:
        messages.success(request, ("That Category Doesn't Exist."))
        return redirect('home')


def product(request,pk):
    product = Product.objects.get(id=pk)
    return render(request, 'product.html', {'product':product})

def home(request):
    products = Product.objects.all()
    return render(request, 'home.html', {'products':products})

def help(request):
    # Retrieve all questions from the model and reverse the order
    questions = Help.objects.all().order_by('-id')

    # Check if the form is submitted
    if request.method == 'POST':
        form = HelpForm(request.POST)
        if form.is_valid():
            form.save()
            # Reinitialize the form with an empty CharField after saving
            form = HelpForm()
    else:
        form = HelpForm()

    return render(request, 'help.html', {'form': form, 'questions': questions[:5]})

def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, ("You Have Been Logged In."))
            return redirect('home')
        else:
            messages.success(request, ("There Was An Error, Please Try Again."))
            return redirect('login')
    else:
        return render(request, 'login.html', {})

def logout_user(request):
    logout(request)
    messages.success(request,("You Have Been Logged Out."))
    return redirect('home')

def register_user(request):
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            #form.save()
            user = User.objects.create_user(
                username = form.cleaned_data['username'],
                password = form.cleaned_data['password1']  
            )
            customer = Customer.objects.create(
                user=user,
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                password = form.cleaned_data['password1']  
            )
            # log in user
            login(request, user)
            messages.success(request, ("You Have Successfully Created An Account."))
            return redirect('home')
        else:
            messages.success(request, ("Oops! There Was A Problem Registering Your Account, Please Try Again"))
            return redirect('register')
    else:
        return render(request, 'register.html', {'form':form})
    
def add_to_cart(request, pk):
    product = get_object_or_404(Product, id=pk)
    # Get the current cart from the session
    cart = request.session.get('cart', {})

    print("Cart",cart)
    # Increment the quantity for the product in the cart
    product.id = str(product.id)
    cart[product.id] = cart.get(product.id, 0) + 1
    print("Product count",cart.get(product.id, 0))
    # Save the updated cart back to the session
    request.session['cart'] = cart
    print("Cart",cart)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'message': 'Product added to cart successfully',
            'cart': request.session.get('cart', {}),
        }, content_type='application/json')
    
    messages.success(request, "Product added to cart successfully")
    return redirect( 'product', product.id )

def remove_from_cart(request, pk):
    cart = request.session.get('cart', {})

    # Check if the product is in the cart
    if str(pk) in cart:
        del cart[str(pk)]
        request.session['cart'] = cart
        messages.success(request, "Item removed from cart.")
    else:
        messages.error(request, "Item not found in cart.")

    return redirect('view_cart')  # Redirect to the view cart page

def cart_count(request):
    cart_data = request.session.get('cart', {})
    total_quantity = sum(cart_data.values())
    return JsonResponse({'cart_count': total_quantity})

def view_cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        subtotal = product.price * quantity
        total_price += subtotal
        tax = (total_price * Decimal(str(0.0625)))
        tax =  tax.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        total_price = tax + total_price
        total_price = total_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,
        })

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'cart_items': cart_items,
            'total_price': total_price,
            'tax': tax,
        })

    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price, 'tax': tax})

def checkout(request):
    # Retrieve cart information from the session
    cart = request.session.get('cart', {})

    # Check if the user has a Customer instance
    if hasattr(request.user, 'customer') and request.user.customer:
        customer = request.user.customer
    else:
        # Handle the case where the user doesn't have a Customer instance
        # You might want to redirect to a page where the user can create a profile.
        messages.error(request, "Please Login to Checkout.")
        return redirect('login') 

    # Handle the checkout form submission
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        print(form.errors)
        if form.is_valid():
            # Process the form data (save to database, etc.)
            try:
                with transaction.atomic():
                    # 1. Create an Order instance
                    order = Order.objects.create(
                        customer=customer,
                        total_amount=0,  # Update later
                        order_date=timezone.now(),
                        is_completed=False,
                        full_name=form.cleaned_data['full_name'],
                        address_line1=form.cleaned_data['address_line1'],
                        address_line2=form.cleaned_data['address_line2'],
                        city=form.cleaned_data['city'],
                        state=form.cleaned_data['state'],
                        postal_code=form.cleaned_data['postal_code'],
                        country=form.cleaned_data['country'],
                    )
                    # 2. Create OrderItem instances
                    for product_id, quantity in cart.items():
                        product = get_object_or_404(Product, id=int(product_id))
                        item_price = product.price * quantity

                        order_item = OrderItem.objects.create(
                            order=order,
                            product=product,
                            quantity=quantity,
                            item_price=item_price,
                        )

                    # 3. Update the order's total_amount
                    order.total_amount = sum(item * Product.objects.get(id=int(product_id)).price for product_id, item in cart.items())
                    order.save()

                    # Clear the cart after the order is created
                    request.session['cart'] = {}

                return redirect('payment_confirmation', order_id=order.id)  # Redirect to the next step in the checkout process

            except Exception as e:
                # Handle any exceptions (e.g., database errors)
                print(f"Error creating order: {e}")
                messages.error(request, "Error creating order. Please try again.")
    else:
        form = CheckoutForm()

    # Retrieve product details based on cart items
    cart_items = []
    total_price = 0

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=int(product_id))
        subtotal = product.price * quantity
        total_price += subtotal

        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,
            'checkout_form': form,
        })

    return render(request, 'checkout.html', {'cart_items': cart_items, 'total_price': total_price, 'checkout_form': form})

def payment_confirmation(request, order_id):
    order = Order.objects.get(id=order_id)
    return render(request, 'payment_confirmation.html', {'order':order})

def view_orders(request):
    # Check if the user has a Customer instance
    if hasattr(request.user, 'customer') and request.user.customer:
        customer = request.user.customer
    else:
        # Handle the case where the user doesn't have a Customer instance
        # You might want to redirect to a page where the user can create a profile.
        messages.error(request, "Please Login to View Orders.")
        return redirect('login') 

    # Continue with your logic for authenticated users
    orders = Order.objects.filter(customer=customer).order_by('-order_date')
    context = {'orders': orders}

    return render(request, 'orders.html', context)

def view_order_details(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'order_details.html', {'order': order})

def search(request):
    query = request.GET.get('q')

    if query:
        results = Product.objects.filter(name__icontains=query)

    else:
        results = None

    return render(request, 'search_results.html', {'results': results, 'query': query})