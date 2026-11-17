from decimal import Decimal
from django.db.models import Avg, Count, F, Sum
from catalog.models import Filling
from orders.models import Order, OrderItem
from production.models import ProductionDay


def run_five_queries():
   
    q1 = ProductionDay.objects.filter(
        booked_weight_kg__gt=Decimal('0.00'),
        max_weight_kg__lte=F('booked_weight_kg') + Decimal('10.00'),
    )
    print('=== ЗАПРОС 1 (Фильтрация) ===')
    print('SQL:', q1.query)
    for shift in q1:
        print(f'  Дата: {shift.shift_date} | Занято: {shift.booked_weight_kg}/{shift.max_weight_kg} кг')

   
    q2 = Filling.objects.filter(
        is_active=True,
        price_per_kg__lt=Decimal('2200.00'),
    ).order_by('price_per_kg', 'name')
    print('\n=== ЗАПРОС 2 (Сортировка) ===')
    print('SQL:', q2.query)
    for f in q2:
        print(f'  {f.name}: {f.price_per_kg} руб./кг')

   
    q3_qs = Order.objects.exclude(status=Order.Status.CANCELLED)
    stats = q3_qs.aggregate(
        total_orders=Count('id'),
        total_revenue=Sum('total_price'),
        avg_check=Avg('total_price'),
        avg_weight=Avg('total_weight_kg'),
    )
    print('\n=== ЗАПРОС 3 (Агрегация Count, Sum, Avg) ===')
    print('SQL:', q3_qs.values('id').query)
    print('Результат:', stats)

   
    q4 = Order.objects.select_related(
        'customer',
        'customer__profile',
        'production_day',
        'production_day__pastry_chef',
    ).filter(
        status__in=[Order.Status.PREPAID, Order.Status.IN_PROGRESS]
    )
    print('\n=== ЗАПРОС 4 (Связь 1:N + select_related) ===')
    print('SQL:', q4.query)
    for o in q4[:5]:
        print(
            f'  Заказ {o.order_number} | Клиент: {o.customer.last_name} '
            f'| Дата смены: {o.production_day.shift_date} '
            f'| Кондитер: {o.production_day.pastry_chef.last_name}'
        )

  
    q5 = OrderItem.objects.select_related(
        'order',
        'filling',
        'sponge_type',
    ).prefetch_related(
        'decors',
        'item_decors__decor',
    ).all()
    print('\n=== ЗАПРОС 5 (Связь M:N + prefetch_related) ===')
    print('SQL:', q5.query)
    for item in q5[:5]:
        decor_names = ', '.join(d.name for d in item.decors.all()) or 'Без доп. декора'
        print(
            f'  Заказ {item.order.order_number}: {item.filling.name} '
            f'({item.weight_kg} кг) | Декор: {decor_names} | Итого: {item.item_price} руб.'
        )


if __name__ == '__main__':
    run_five_queries()
