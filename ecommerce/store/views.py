from django.shortcuts import render, redirect
from .models import Product, Category
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm
from django import forms
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# def home(request):
#     products = Product.objects.all()
#     if request.GET.get('search'):
#         products = products.filter(name__icontains=request.GET.get('search'))
#     return render(request, 'home.html', {'products':products})

def home(request):
    products = Product.objects.all()
    paginator = Paginator(products, 4)

    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(name__icontains=search_query)


    return render(request, 'home.html', {'page_obj':page_obj, 'search_query':search_query})



def about(request):
    return render(request, 'about.html', {})


def products(request):
    return render(request, 'products.html', {})
    

def product_details(request, pk):
    product = Product.objects.get(id=pk)
    return render(request, 'product_details.html', {'product':product})


def categories(request):
    return render(request,'categories.html',{})



def category(request,cat):
    try:
        category = Category.objects.get(name=cat)
        products = Product.objects.filter(category=category)

        paginator = Paginator(products, 2)

        page_number = request.GET.get('page')
        try:
            page_obj = paginator.get_page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        
        return render(request, 'category.html', {'category':category, 'page_obj':page_obj})

    except:
        messages.success(request,('That category doesnt existt'))
        return redirect('home')



def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username= username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'You have successfully logged in!')
            return redirect('home')
        else:
            messages.error(request, 'Error logging in, please try again...')
            return redirect('login')

    else:
        return render(request, 'login.html', {})

        
def logout_user(request):
    logout(request)
    messages.success(request, 'You have successfully logged out!')
    return redirect('home')

def register_user(request):
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            #login user
            user = authenticate(username=username, password=password)
            login(request,user)
            messages.success(request, ("Registration Successful! You are now logged in."))
            return redirect('home')
        else:
            messages.warning(request, ("whoops! something went wrong - please try again..."))
            return render(request, 'register.html', {'form': form})
    else:
        return render(request, 'register.html',{'form':form})