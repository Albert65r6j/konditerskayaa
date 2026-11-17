from django.shortcuts import render

def reviews_list(request):
    return render(request, 'catalog/index.html')
