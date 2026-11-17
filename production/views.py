from django.shortcuts import render

def kitchen_schedule(request):
    return render(request, 'catalog/index.html')
