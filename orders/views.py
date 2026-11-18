from django.shortcuts import render
from catalog.models import BaseCake, Decor, Filling, SpongeType
from orders.models import Order
from production.models import ProductionDay


def order_constructor(request):
    base_cake_id = request.GET.get('base_cake')
    selected_cake = BaseCake.objects.filter(pk=base_cake_id, is_active=True).first() if base_cake_id else None
    return render(request, 'orders/constructor.html', {
        'selected_cake': selected_cake,
        'sponges': SpongeType.objects.filter(is_active=True),
        'fillings': Filling.objects.filter(is_active=True),
        'decors': Decor.objects.filter(is_active=True),
        'production_days': ProductionDay.objects.filter(is_closed=False).order_by('work_date')[:14],
    })


def my_orders(request):
    if request.user.is_authenticated:
        orders = Order.objects.filter(client=request.user).select_related('production_day').prefetch_related('items').order_by('-created_at')
    else:
        orders = Order.objects.select_related('production_day', 'client').prefetch_related('items').order_by('-created_at')[:10]
    return render(request, 'orders/my_orders.html', {'orders': orders})
