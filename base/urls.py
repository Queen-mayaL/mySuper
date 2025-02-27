from django.contrib import admin
from django.urls import path
from .views import MyTokenObtainPairView
from . import views

urlpatterns = [
    path('api/products/category/<int:category_id>/', views.get_products_by_category),
    path('login/', MyTokenObtainPairView.as_view()),
    path('register/', views.register),
    path('add_new_order/', views.add_new_order),
    path('add_to_cart/', views.add_to_cart),
    path('get_top_5_user_interests/', views.get_top_5_user_interests),
    
]
