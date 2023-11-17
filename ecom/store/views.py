from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import *
from django.http import JsonResponse
from django.contrib.auth.models import User

def category(request,cate):
    #replace Hypens with Spaces
    #cate = cate.replace('-', '')
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

def about(request):
    return render(request, 'about.html', {})

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
    cart[str(product.id)] = cart.get(str(product.id), 0) + 1
    print("Product count",cart.get(str(product.id), 0))
    # Save the updated cart back to the session
    request.session['cart'] = cart
    print("Cart",cart)
    return JsonResponse({
        'message': 'Product added to cart successfully',
        'cart': request.session.get('cart', {}),
    })
    #messages.success(request, "Product added to cart successfully")
    #return redirect( 'product', product.id )

def view_cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        subtotal = product.price * quantity
        total_price += subtotal

        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,
        })

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'cart_items': cart_items,
            'total_price': total_price,
        })

    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})

def checkout(request):
    # Retrieve cart information from the session
    cart = request.session.get('cart', [])

    # Handle the checkout form submission
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Process the form data (save to database, etc.)
            #form_data = form.cleaned_data
            order = form.save()
            # ... (handle the form data as needed)
            return redirect('payment_confirmation')  # Redirect to the next step in the checkout process
    else:
        form = CheckoutForm()

    # Retrieve product details based on cart items
    cart_items = []
    total_price = 0

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        subtotal = product.price * quantity
        total_price += subtotal

        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,
		    'checkout_form': form,
        })
    return render(request, 'checkout.html', {'cart_items': cart_items, 'total_price': total_price})

def payment_confirmation(request):
    # Perform any additional processing related to payment confirmation
    # ...
    return render(request, 'payment_confirmation.html')

def cart_count(request):
    cart_data = request.session.get('cart', {})
    total_quantity = sum(cart_data.values())
    return JsonResponse({'cart_count': total_quantity})