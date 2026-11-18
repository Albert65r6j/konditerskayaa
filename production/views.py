from django.shortcuts import render
from production.models import ProductionDay


def kitchen_schedule(request):
    days = ProductionDay.objects.prefetch_related('orders__items').order_by('work_date')
    return render(request, 'production/schedule.html', {'days': days})
