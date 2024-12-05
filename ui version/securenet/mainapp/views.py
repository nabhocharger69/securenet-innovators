from django.shortcuts import render

def landing_page(request):
    return render(request, 'landing.html')

def products_page(request):
    return render(request, 'products.html')

