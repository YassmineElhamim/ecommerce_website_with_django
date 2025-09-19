from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('categories/', views.categories, name='categories'),
    path('products/', views.products, name='products'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/',views.register_user, name='register'),
    path('product/<int:pk>', views.product_details, name='product_details'),
    path('category/<str:cat>', views.category, name='category'),
]
