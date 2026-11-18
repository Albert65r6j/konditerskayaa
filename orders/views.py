from decimal import Decimal
import uuid
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from catalog.models import BaseCake, Decor
from orders.forms import OrderConstructorForm
from orders.models import DesignSketch, Order, OrderItem, OrderItemDecor
from production.models import ProductionDay

User = get_user_model()


def order_constructor(request):
    base_cake_id = request.GET.get('base_cake')
    selected_cake = BaseCake.objects.filter(pk=base_cake_id, is_active=True).first() if base_cake_id else None

    if request.method == 'POST':
        form = OrderConstructorForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                day = ProductionDay.objects.select_for_update().get(pk=form.cleaned_data['production_day'].pk)
                weight = form.cleaned_data['weight_kg']
                remaining = day.max_weight_kg - day.booked_weight_kg
                if remaining < weight:
                    messages.error(request, 'К сожалению, свободный лимит цеха на эту дату только что закончился.')
                else:
                    customer = request.user if request.user.is_authenticated else User.objects.first()
                    address = form.cleaned_data['delivery_address'].strip()
                    delivery_type = 'DELIVERY' if address and 'самовывоз' not in address.lower() else 'PICKUP'

                    order = Order.objects.create(
                        order_number=f"ORD-{uuid.uuid4().hex[:6].upper()}",
                        customer=customer,
                        production_day=day,
                        delivery_type=delivery_type,
                        delivery_address=address or 'Самовывоз из студии',
                    )

                    item = OrderItem.objects.create(
                        order=order,
                        base_cake=selected_cake,
                        sponge_type=form.cleaned_data['sponge'],
                        filling=form.cleaned_data['filling'],
                        weight_kg=weight,
                        inscription_text=form.cleaned_data['inscription'],
                    )

                    for decor in form.cleaned_data['decors']:
                        OrderItemDecor.objects.create(
                            order_item=item,
                            decor=decor,
                            applied_surcharge=decor.surcharge
                        )




                    calculated = item.calculate_price()
                    item.save()

                    item_sum = getattr(item, 'item_total', None) or getattr(item, 'item_price', None) or calculated or Decimal('0')
                    order.total_weight_kg = weight
                    order.total_price = item_sum
                    order.save()


                    day.booked_weight_kg += weight
                    day.save()

                    if form.cleaned_data.get('sketch'):
                        sketch_fields = {f.name for f in DesignSketch._meta.fields}
                        sketch_kwargs = {'order_item': item}
                        if 'image' in sketch_fields:
                            sketch_kwargs['image'] = form.cleaned_data['sketch']
                        elif 'sketch_file' in sketch_fields:
                            sketch_kwargs['sketch_file'] = form.cleaned_data['sketch']
                        if 'comment' in sketch_fields:
                            sketch_kwargs['comment'] = 'Эскиз клиента из онлайн-конструктора'
                        elif 'description' in sketch_fields:
                            sketch_kwargs['description'] = 'Эскиз клиента из онлайн-конструктора'
                        DesignSketch.objects.create(**sketch_kwargs)


                    messages.success(request, f'Заказ № {order.order_number} успешно оформлен на сумму {order.total_price:.0f} ₽!')
                    return redirect('my_orders')
        else:
            messages.error(request, 'Проверьте правильность заполнения полей формы заказа.')
    else:
        initial = {}
        if selected_cake:
            initial = {
                'sponge': selected_cake.default_sponge_id,
                'filling': selected_cake.default_filling_id,
                'weight_kg': selected_cake.min_weight_kg,
            }
        form = OrderConstructorForm(initial=initial)

    return render(request, 'orders/constructor.html', {
        'form': form,
        'selected_cake': selected_cake,
        'decors': Decor.objects.filter(is_active=True),
    })


def my_orders(request):
    if request.user.is_authenticated:
        orders = Order.objects.filter(customer=request.user).select_related('production_day').prefetch_related('items').order_by('-created_at')
    else:
        orders = Order.objects.select_related('production_day', 'customer').prefetch_related('items').order_by('-created_at')[:10]
    return render(request, 'orders/my_orders.html', {'orders': orders})


def api_check_capacity(request):
    day_id = request.GET.get('day_id')
    weight_raw = request.GET.get('weight', '2.0')
    day = get_object_or_404(ProductionDay, pk=day_id)
    try:
        requested_weight = Decimal(weight_raw)
    except Exception:
        requested_weight = Decimal('2.0')

    remaining = day.max_weight_kg - day.booked_weight_kg
    available = float(remaining)
    is_enough = remaining >= requested_weight
    return JsonResponse({
        'date': day.shift_date.strftime('%d.%m.%Y'),
        'max_weight': float(day.max_weight_kg),
        'booked_weight': float(day.booked_weight_kg),
        'remaining_weight': available,
        'is_enough': is_enough,
        'message': f'Свободно {available:.1f} кг из {float(day.max_weight_kg):.1f} кг' if is_enough else f'Недостаточно квоты! Осталось {available:.1f} кг.'
    })
