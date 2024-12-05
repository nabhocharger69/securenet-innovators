from django.urls import path
from . import views  # Import views from the current app
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.landing_page, name='landing'),  # Route for the home page
    path('products', views.products_page, name='products'), 
]

