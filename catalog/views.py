from django.shortcuts import render
from catalog.models import BaseCake
from reviews.models import Review

def index(request):
    featured_cakes = BaseCake.objects.filter(is_active=True).select_related('default_filling', 'default_sponge')[:4]
    latest_reviews = Review.objects.filter(is_published=True).select_related('author', 'order')[:3]
    context = {
        'featured_cakes': featured_cakes,
        'latest_reviews': latest_reviews,
    }
    return render(request, 'catalog/index.html', context)

def catalog_list(request):
    cakes = BaseCake.objects.filter(is_active=True).select_related('default_filling', 'default_sponge')
    return render(request, 'catalog/catalog_list.html', {'cakes': cakes})
