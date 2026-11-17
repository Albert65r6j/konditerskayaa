from django.shortcuts import render

def order_constructor(request):
    return render(request, 'catalog/index.html')

def my_orders(request):
    return render(request, 'catalog/index.html')
