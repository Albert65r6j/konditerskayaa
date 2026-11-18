from django.core.paginator import Paginator
from django.shortcuts import render
from reviews.models import Review


def reviews_list(request):
    reviews_qs = Review.objects.filter(is_published=True).select_related('author', 'order').order_by('-created_at')
    paginator = Paginator(reviews_qs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'reviews/reviews_list.html', {'page_obj': page_obj})
