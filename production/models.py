from decimal import Decimal
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import F, Q




class ProductionDay(models.Model):

    shift_date = models.DateField(
        unique=True,
        verbose_name='Дата производственной смены',
    )
    pastry_chef = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='production_shifts',
        verbose_name='Ответственный кондитер',
    )
    max_weight_kg = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal('25.00'),
        validators=[MinValueValidator(Decimal('1.00'))],
        verbose_name='Суточный лимит веса цеха (кг)',
    )
    booked_weight_kg = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Забронированный вес (кг)',
    )
    notes = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Примечание к смене',
    )

    class Meta:
        db_table = 'production_productionday'
        verbose_name = 'Производственная смена'
        verbose_name_plural = 'Производственные смены'
        ordering = ['shift_date']
        constraints = [
            models.CheckConstraint(
                condition=Q(booked_weight_kg__gte=0) & Q(booked_weight_kg__lte=F('max_weight_kg')),
                name='chk_productionday_weight_within_limit',
            ),
        ]

    @property
    def remaining_weight_kg(self) -> Decimal:
        return max(Decimal('0.00'), self.max_weight_kg - self.booked_weight_kg)

    def __str__(self):
        return f'Смена {self.shift_date:%d.%m.%Y}: {self.booked_weight_kg}/{self.max_weight_kg} кг'