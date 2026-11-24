import logging
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from production.models import ProductionDay

logger = logging.getLogger('bakery.production')


def kitchen_schedule(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        logger.warning('Попытка несанкционированного доступа к графику цеха: пользователь %s', request.user)
        raise PermissionDenied('Доступ разрешён только сотрудникам кондитерского цеха.')
    days = ProductionDay.objects.prefetch_related('orders__items').order_by('shift_date')
    return render(request, 'production/schedule.html', {'days': days})
