import json
from pyexpat.errors import messages
from django.shortcuts import render

# Create your views here.
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.forms import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .models import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404, HttpResponse, JsonResponse
from django.db.models.functions import Random
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import openai, os
from openai import OpenAI
from dotenv import load_dotenv
import cohere
load_dotenv()


cohere_key = os.getenv("COHERE_KEY")



@login_required
def cart_item_count(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'User not authenticated'}, status=401)
    
    cart_items = Cart.objects.filter(user=request.user)
    total_items = sum(item.quantity for item in cart_items)
    return JsonResponse({'total_items': total_items})

@login_required
def remove_from_cart(request, item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(Cart, id=item_id, user=request.user)
        cart_item.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request'})


def home_view(request):

    products = Product.objects.all()
    product_list = [f"{product.name}: {product.description} price: {product.price} id: {product.id}" for product in products]

    if not cohere_key:
        return JsonResponse({'error': 'Cohere API key is not set'}, status=500)
    
    co = cohere.Client(cohere_key)
    

    processors = Product.objects.filter(category=1)
    cards = Product.objects.filter(category=2)
    laptops = Product.objects.filter(category=5)
    keyboards = Product.objects.filter(category=4)

    prompt_base = 'Eres un experto en computadores, tu nombre es pc guru'
    if 'chat_messages' not in request.session:
        request.session['chat_messages'] = []

    chat_messages = request.session['chat_messages']

    if request.method == 'POST':
        user_message = request.POST.get('user_input')
        if user_message:
            chat_messages.append({'sender': 'user', 'text': user_message})
            try:
                response = co.chat(
                    model="command-r-plus",
                    temperature=0.7,
                    stop_sequences= ["usuario:"],    
                    preamble = f"""
                                PC Guru, eres el bot oficial para JPC, un ecommerce especializado en componentes de PC de gama media-alta. Tu misión es proporcionar recomendaciones personalizadas, responder preguntas técnicas sobre hardware y facilitar el proceso de compra. Tu objetivo es mejorar la experiencia del usuario ofreciendo conocimientos especializados y asistencia práctica en la selección de productos tecnológicos.
                                A continuación, se proporciona una lista de productos disponibles: {', '.join(product_list)}. Cuando recomiendes un producto, siempre incluye el enlace al producto correspondiente en el formato HTML. El formato del enlace es: <a href="http://127.0.0.1:8000/product/<ID_DEL_PRODUCTO>">Product Link</a>.
                                Recuerda siempre proporcionar enlaces precisos y asegurar que tus respuestas sean claras y útiles para el usuario.
                                Ejemplo de respuesta correcta:
                                - Aquí tienes un enlace a nuestra tarjeta gráfica NVIDIA GeForce RTX 4070 SUPER TRINITY 12GB BLACK EDITION: <a href="http://127.0.0.1:8000/product/254">Link</a>
                                Usuario: {user_message}
                                PC Guru:""",
                    message=user_message,
                                        
                )
                chat_messages.append({'sender': 'bot', 'text': response.text})
            except:
                chat_messages.append({'sender': 'bot', 'text': 'In this moment i am not online'})
            
            request.session['chat_messages'] = chat_messages
            
            return JsonResponse({'chat_messages': chat_messages})

    return render(request, 'home.html', {
        'processors': processors,
        'cards': cards,
        'laptops': laptops,
        'keyboards': keyboards,
        'chat_messages': chat_messages,
    })


def components_view (request):

    products_list = Product.objects.all()
    
    order_by = request.GET.get('order', '')
    
    if order_by == 'higher-price':
        products_list = products_list.order_by('-price')
    elif order_by == 'lower-price':
        products_list = products_list.order_by('price')
    
    
    paginator = Paginator(products_list, 32)

    page_number = request.GET.get('page')

    try:
        products = paginator.page(page_number)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    return render(request, 'components.html', {
        'products': products,
        'current_page': page_number,
        'order': order_by
    })
   


def processors_view(request):

    # SQL query for get all processors and their data
    processors_list = Product.objects.filter(category = 1)
    
    order_by = request.GET.get('order', '')
    
    if order_by == 'higher-price':
        processors_list = processors_list.order_by('-price')
    elif order_by == 'lower-price':
        processors_list = processors_list.order_by('price')

    paginator = Paginator(processors_list, 12)

    page_number = request.GET.get('page')

    try:
        products = paginator.page(page_number)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    return render(request, 'processors.html', {
        'products' : products,
        'current_page': page_number,
        'order': order_by
        
    })

def graphics_view (request):

    # SQL Query for get all graphis cards and their data

    cards = Product.objects.filter(category = 2)
    
    order_by = request.GET.get('order', '')
    
    if order_by == 'higher-price':
        cards = cards.order_by('-price')
    elif order_by == 'lower-price':
        cards = cards.order_by('price')

    return render(request, 'gpu.html', {
        'products' : cards
    })

def ram_view (request):

    # SQL Query for get all ram and their data

    ram = Product.objects.filter(category = 3)
    
    order_by = request.GET.get('order', '')
    
    if order_by == 'higher-price':
        ram = ram.order_by('-price')
    elif order_by == 'lower-price':
        ram = ram.order_by('price')

    return render(request, 'rams.html',  {
        'products': ram
    })

def motherboards_view (request):

    # SQL Query for get all motherboards ant their data
    motherboard_list = Product.objects.filter(category = 6)
    
    order_by = request.GET.get('order', '')
    
    if order_by == 'higher-price':
        motherboard_list = motherboard_list.order_by('-price')
    elif order_by == 'lower-price':
        motherboard_list = motherboard_list.order_by('price')

    paginator = Paginator(motherboard_list,12)

    page_number = request.GET.get('page')

    try:
        products = paginator.page(page_number)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    return render(request, 'motherboards.html', {
        'products': products,
        'current_page': page_number,
        'order': order_by
    })

def storage_view (request):
    
    # SQL Query for get all SDD, M.2 ant their data
    storage_list = Product.objects.filter(category = 7)
    
    order_by = request.GET.get('order', '')
    
    if order_by == 'higher-price':
        storage_list = storage_list.order_by('-price')
    elif order_by == 'lower-price':
        storage_list = storage_list.order_by('price')

    paginator = Paginator(storage_list,12)

    page_number = request.GET.get('page')

    try:
        products = paginator.page(page_number)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    return render(request, 'storage.html', {
        'products': products,
        'current_page': page_number,
        'order': order_by
    })

def power_view (request):

    # SQL Query for get all SDD, M.2 ant their data
    power_list = Product.objects.filter(category = 8)
    
    order_by = request.GET.get('order', '')
    
    if order_by == 'higher-price':
        power_list = power_list.order_by('-price')
    elif order_by == 'lower-price':
        power_list = power_list.order_by('price')

    paginator = Paginator(power_list,12)

    page_number = request.GET.get('page')

    try:
        products = paginator.page(page_number)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    return render(request, 'power.html', {
        'products': products,
        'current_page': page_number,
        'order': order_by
    })

def case_view (request):

    # SQL Query for get all SDD, M.2 ant their data
    case_list = Product.objects.filter(category = 9)
    
    order_by = request.GET.get('order', '')
    
    if order_by == 'higher-price':
        case_list= case_list.order_by('-price')
    elif order_by == 'lower-price':
        case_list = case_list.order_by('price')

    paginator = Paginator(case_list,12)

    page_number = request.GET.get('page')

    try:
        products = paginator.page(page_number)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    return render(request, 'case.html', {
        'products': products,
        'current_page': page_number,
        'order': order_by
    })

def headphones_view (request):

    # SQL Query for get all headphones and their data
    headphone_list = Product.objects.filter(category = 10)
    
    order_by = request.GET.get('order', '')
    
    if order_by == 'higher-price':
        headphone_list = headphone_list.order_by('-price')
    elif order_by == 'lower-price':
        headphone_list = headphone_list.order_by('price')

    paginator = Paginator(headphone_list,12)

    page_number = request.GET.get('page')

    try:
        products = paginator.page(page_number)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    return render(request, 'headphones.html', {
        'products': products,
        'current_page': page_number,
        'order': order_by
    })


def keyboard_view (request):

    keyboard_list = Product.objects.filter(category = 4)
    
    order_by = request.GET.get('order', '')
    
    if order_by == 'higher-price':
        keyboard_list = keyboard_list.order_by('-price')
    elif order_by == 'lower-price':
        keyboard_list = keyboard_list.order_by('price')

    paginator = Paginator(keyboard_list,12)

    page_number = request.GET.get('page')

    try:
        products = paginator.page(page_number)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    return render(request, 'keyboard.html', {
        'products': products,
        'current_page': page_number,
        'order': order_by
    })

def refrigeration_view (request):

    refrigeration_list = Product.objects.filter(category = 11)
    
    order_by = request.GET.get('order', '')
    
    if order_by == 'higher-price':
        refrigeration_list = refrigeration_list.order_by('-price')
    elif order_by == 'lower-price':
        refrigeration_list = refrigeration_list.order_by('price')

    paginator = Paginator(refrigeration_list,12)

    page_number = request.GET.get('page')

    try:
        products = paginator.page(page_number)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    return render(request, 'refrigeration.html', {
        'products': products,
        'current_page': page_number,
        'order': order_by
    })

def monitor_view(request):

    monitor_list = Product.objects.filter(category = 12)
    
    order_by = request.GET.get('order', '')
    
    if order_by == 'higher-price':
        monitor_list = monitor_list.order_by('-price')
    elif order_by == 'lower-price':
        monitor_list = monitor_list.order_by('price')

    paginator = Paginator(monitor_list,12)

    page_number = request.GET.get('page')

    try:
        products = paginator.page(page_number)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    return render(request, 'monitor.html', {
        'products': products,
        'current_page': page_number,
        'order': order_by
    })

def chair_view (request):
    
    chair_list = Product.objects.filter(category = 13)
    
    order_by = request.GET.get('order', '')
    
    if order_by == 'higher-price':
        chair_list = chair_list.order_by('-price')
    elif order_by == 'lower-price':
        chair_list = chair_list.order_by('price')

    paginator = Paginator(chair_list,12)

    page_number = request.GET.get('page')

    try:
        products = paginator.page(page_number)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    return render(request, 'chairs.html', {
        'products': products,
        'current_page': page_number,
        'order': order_by
    })


def accesory_view (request):

    accesory_list = Product.objects.filter(category = 14)
    
    order_by = request.GET.get('order', '')
    
    if order_by == 'higher-price':
        accesory_list = accesory_list.order_by('-price')
    elif order_by == 'lower-price':
        accesory_list = accesory_list.order_by('price')

    paginator = Paginator(accesory_list,8)

    page_number = request.GET.get('page')

    try:
        products = paginator.page(page_number)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    return render(request, 'accessories.html', {
        'products': products,
        'current_page': page_number,
        'order': order_by
    })

def prebuilds_view(request):
    return render(request, 'prebuilds.html')

def laptops_view (request):
    
    laptops_list = Product.objects.filter(category = 5)
    
    order_by = request.GET.get('order', '')
    
    if order_by == 'higher-price':
        laptops_list = laptops_list.order_by('-price')
    elif order_by == 'lower-price':
        laptops_list = laptops_list.order_by('price')

    paginator = Paginator(laptops_list,12)

    page_number = request.GET.get('page')

    try:
        products = paginator.page(page_number)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    return render(request, 'laptops.html', {
        'products': products,
        'current_page': page_number,
        'order': order_by
    })
    

        
    
def sign_up_view (request):
    
    if request.method == 'GET':
        return render(request, 'sign_up.html', {
            'form' : UserCreationForm
        })
        
    else:
        # If the method is not get is a post method
        # Validate if the passwords match 
        if request.POST['password1'] == request.POST['password2']:
            # Try to create a user with the user data and save it
            try:
                user =  User.objects.create_user(username=request.POST['username'], password=request.POST['password1'])
                user.save()
                # Create a session to the user registered
                login(request, user)
                # Redirect to the home view
                return redirect('home')
            # try to catch the integrity error
            # The integrity error is when the user try to sign up but he is already created
            except IntegrityError:
                return render(request, 'login.html',  {
                    'form' : UserCreationForm, 
                    'error': 'UserName Already Exists'
                })
        else:
            return render(request, 'sign_up.html', {
                'form': UserCreationForm,
                'error': 'Passwords do Not Match'
            })

def sign_out (request):
    logout(request)
    return redirect('home')

def login_view(request):
    if request.method == 'GET':
        next_url = request.GET.get('next', '')
        print(f"GET - next: {next_url}")
        return render(request, 'login.html', {
            'form': AuthenticationForm(),
            'next': next_url
        })
    else:
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.POST.get('next')
            print(f"POST - next: {next_url}")
            if next_url:
                return redirect(next_url)
            return redirect('home')
        else:
            next_url = request.POST.get('next', '')
            print(f"POST - next (error): {next_url}")
            return render(request, 'login.html', {
                'form': form,
                'error': 'Username or password is incorrect',
                'next': next_url
            })

def product_view(request, product_id):


    product = get_object_or_404(Product, id=product_id)
    
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity <=0:
            quantity = 1
            
            
        cartItem, created = Cart.objects.get_or_create(user = request.user, product = product, defaults={'quantity': quantity} )
        
        if not created:
            cartItem.quantity += quantity
            cartItem.save()
        else:
            cartItem.quantity = quantity
            cartItem.save()
            
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        
    
    
    return render(request, 'product.html',  {
        'product': product
    })



def cart_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        item_id = data.get('item_id')
        quantity = data.get('quantity')
        if item_id and quantity:
            try:
                cart_item = Cart.objects.get(id=item_id, user=request.user)
                cart_item.quantity = int(quantity)
                cart_item.save()
                return JsonResponse({'success': True})
            except Cart.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Item not found'})
        else:
            return JsonResponse({'success': False, 'error': 'Invalid data'})
    else:
        cart_items = Cart.objects.filter(user=request.user)
        quantity_range = range(1, 16) 
        return render(request, 'cart.html', {
            'cart': cart_items,
            'quantity_range': quantity_range
        })
