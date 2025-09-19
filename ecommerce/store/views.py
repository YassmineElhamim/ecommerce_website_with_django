from django.shortcuts import render, redirect
from .models import Product, Category
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from.forms import SignUpForm
from django import forms


def home(request):
    products = Product.objects.all()
    return render(request, 'home.html', {'products':products})



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
        return render(request, 'category.html', {'category':category, 'products':products})

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
            messages.success(request, 'Error logging in, please try again...')
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
            messages.success(request, ("whoops! something went wrong - please try again..."))
            return render(request, 'register.html', {'form': form})
    else:
        return render(request, 'register.html',{'form':form})