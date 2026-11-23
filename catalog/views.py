from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from catalog.models import BaseCake, Filling
from reviews.models import Review


def index(request):
    featured_cakes = BaseCake.objects.filter(is_active=True).select_related('default_filling', 'default_sponge')[:4]
    latest_reviews = Review.objects.filter(is_published=True).select_related('author', 'order')[:3]
    return render(request, 'catalog/index.html', {
        'featured_cakes': featured_cakes,
        'latest_reviews': latest_reviews,
    })


def catalog_list(request):
    cakes_qs = BaseCake.objects.filter(is_active=True).select_related('default_filling', 'default_sponge').order_by('-rating', 'title')
    query = ' '.join(request.GET.get('q', '').split())

    category = request.GET.get('category', '').strip()
    filling_id = request.GET.get('filling', '').strip()

    if query:
        cakes_qs = cakes_qs.filter(Q(title__icontains=query) | Q(description__icontains=query))
    if category:
        cakes_qs = cakes_qs.filter(category=category)
    if filling_id.isdigit():
        cakes_qs = cakes_qs.filter(default_filling_id=int(filling_id))

    paginator = Paginator(cakes_qs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'catalog/catalog_list.html', {
        'page_obj': page_obj,
        'query': query,
        'selected_category': category,
        'selected_filling': filling_id,
        'categories': BaseCake.Category.choices,
        'fillings': Filling.objects.filter(is_active=True),
        'total_count': cakes_qs.count(),
    })


def cake_detail(request, pk):
    cake = get_object_or_404(
        BaseCake.objects.select_related('default_filling', 'default_sponge'),
        pk=pk,
        is_active=True
    )
    related_cakes = BaseCake.objects.filter(is_active=True, category=cake.category).exclude(pk=cake.pk)[:3]
    return render(request, 'catalog/cake_detail.html', {
        'cake': cake,
        'related_cakes': related_cakes,
    })


def about_page(request):
    return render(request, 'catalog/about.html')
