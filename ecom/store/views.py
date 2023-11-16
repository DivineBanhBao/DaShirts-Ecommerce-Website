from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import SignUpForm
from django.http import JsonResponse

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
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            # log in user
            user = authenticate(username=username, password=password)
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

    # Check for the 'X-Requested-With' header to identify AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # For AJAX requests, update the cart and return a JSON response
        cart = request.session.get('cart', [])
        cart.append({'product_id': product.id, 'quantity': 1})
        request.session['cart'] = cart

        return JsonResponse({'message': 'Product added to cart successfully'})
    else:
        # For regular requests, use the simplified logic
        if 'cart' not in request.session:
            request.session['cart'] = []

        cart = request.session['cart']
        cart.append({'product_id': product.id, 'quantity': 1})
        request.session['cart'] = cart

        messages.success(request, "Product added to cart.")
        return redirect('home')

def view_cart(request):
     # Retrieve cart information from the session
    cart = request.session.get('cart', [])

    # Retrieve product details for each item in the cart
    cart_items = []
    total_price = 0

    for item in cart:
        product_id = item['product_id']
        quantity = item['quantity']

        try:
            product = Product.objects.get(id=product_id)
            total_price += product.price * quantity
            cart_items.append({'product': product, 'quantity': quantity})
        except Product.DoesNotExist:
            # Handle the case where the product does not exist
            messages.warning(request, f"Product with ID {product_id} does not exist.")

    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})

def get_cart_number(request):
    # Retrieve cart information from the session
    cart = request.session.get('cart', [])

    # Calculate the total number of items in the cart
    total_items = sum(item['quantity'] for item in cart)

    return JsonResponse({'total_items': total_items})