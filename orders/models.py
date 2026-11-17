from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import F, Q, Sum


from catalog.models import BaseCake, Decor, Filling, SpongeType
from production.models import ProductionDay


def validate_sketch_file_size(value):
    max_size = 5 * 1024 * 1024
    if value.size > max_size:
        raise ValidationError('Размер файла эскиза не должен превышать 5 МБ.')


class Order(models.Model):

    class DeliveryType(models.TextChoices):
        PICKUP = 'pickup', 'Самовывоз из кондитерской'
        COURIER = 'courier', 'Доставка курьером (+2...+6 °C)'

    class Status(models.TextChoices):
        NEW = 'new', 'Новый (ожидает предоплату)'
        PREPAID = 'prepaid', 'Предоплата внесена'
        IN_PROGRESS = 'in_progress', 'В работе у кондитера'
        READY = 'ready', 'Готов к выдаче'
        COMPLETED = 'completed', 'Выдан покупателю'
        CANCELLED = 'cancelled', 'Отменён'

    order_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Номер заказа',
    )
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='orders',
        verbose_name='Покупатель',
    )
    production_day = models.ForeignKey(
        ProductionDay,
        on_delete=models.PROTECT,
        related_name='orders',
        verbose_name='Производственная смена (дата выдачи)',
    )
    delivery_interval = models.CharField(
        max_length=30,
        default='12:00–15:00',
        verbose_name='Интервал выдачи / доставки',
    )
    delivery_type = models.CharField(
        max_length=15,
        choices=DeliveryType.choices,
        default=DeliveryType.PICKUP,
        verbose_name='Способ получения',
    )
    delivery_address = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Адрес доставки',
    )
    total_weight_kg = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Общий вес заказа (кг)',
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Итоговая стоимость (руб.)',
    )
    prepayment_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Сумма предоплаты (руб.)',
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        verbose_name='Статус заказа',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата и время оформления',
    )

    class Meta:
        db_table = 'orders_order'
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(
                condition=Q(total_price__gte=0) & Q(prepayment_amount__gte=0),
                name='chk_order_amounts_non_negative',
            ),
        ]

    def __str__(self):
        return f'Заказ №{self.order_number} от {self.created_at:%d.%m.%Y} ({self.get_status_display()})'


class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Заказ',
    )
    base_cake = models.ForeignKey(
        BaseCake,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_items',
        verbose_name='Базовый торт (если выбран)',
    )
    filling = models.ForeignKey(
        Filling,
        on_delete=models.PROTECT,
        related_name='order_items',
        verbose_name='Начинка',
    )
    sponge_type = models.ForeignKey(
        SpongeType,
        on_delete=models.PROTECT,
        related_name='order_items',
        verbose_name='Вид коржа',
    )
    decors = models.ManyToManyField(
        Decor,
        through='OrderItemDecor',
        related_name='order_items',
        blank=True,
        verbose_name='Выбранный декор',
    )
    weight_kg = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.40')), MaxValueValidator(Decimal('25.00'))],
        verbose_name='Вес торта (кг)',
    )
    inscription_text = models.CharField(
        max_length=120,
        blank=True,
        verbose_name='Поздравительная надпись на торте',
    )
    item_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Рассчитанная стоимость позиции (руб.)',
    )

    class Meta:
        db_table = 'orders_orderitem'
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказов'
        ordering = ['id']
        constraints = [
            models.CheckConstraint(
                condition=Q(weight_kg__gte=Decimal('0.40')) & Q(weight_kg__lte=Decimal('25.00')),
                name='chk_orderitem_weight_range',
            ),
        ]

    def calculate_price(self) -> Decimal:
        """
        Серверный расчёт цены по формуле ТЗ (FR-07):
        Цена = Вес * (Цена_начинки_за_кг + Доплата_за_корж) + Сумма_надбавок_за_декор
        """
        decor_total = (
            self.item_decors.aggregate(total=Sum('applied_surcharge'))['total']
            or Decimal('0.00')
        )
        base_rate = self.filling.price_per_kg + self.sponge_type.extra_price_per_kg
        return (self.weight_kg * base_rate + decor_total).quantize(Decimal('0.01'))

    def __str__(self):
        return f'Торт «{self.filling.name}» ({self.weight_kg} кг) — {self.item_price} руб.'


class OrderItemDecor(models.Model):

    order_item = models.ForeignKey(
        OrderItem,
        on_delete=models.CASCADE,
        related_name='item_decors',
        verbose_name='Позиция заказа',
    )
    decor = models.ForeignKey(
        Decor,
        on_delete=models.PROTECT,
        related_name='item_decors',
        verbose_name='Элемент декора',
    )
    applied_surcharge = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name='Зафиксированная надбавка на момент заказа (руб.)',
    )
    custom_note = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Пожелание к исполнению декора',
    )

    class Meta:
        db_table = 'orders_orderitemdecor'
        verbose_name = 'Декор в позиции заказа'
        verbose_name_plural = 'Декор в позициях заказов'
        constraints = [
            models.UniqueConstraint(
                fields=['order_item', 'decor'],
                name='uq_orderitem_decor_pair',
            ),
        ]

    def __str__(self):
        return f'{self.decor.name} (+{self.applied_surcharge} руб.)'


class DesignSketch(models.Model):

    order_item = models.ForeignKey(
        OrderItem,
        on_delete=models.CASCADE,
        related_name='sketches',
        verbose_name='Позиция заказа',
    )
    image = models.ImageField(
        upload_to='sketches/%Y/%m/',
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp']),
            validate_sketch_file_size,
        ],
        verbose_name='Файл эскиза (JPG/PNG/WEBP, до 5 МБ)',
    )
    comment = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Комментарий к референсу',
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата и время загрузки',
    )

    class Meta:
        db_table = 'orders_designsketch'
        verbose_name = 'Эскиз оформления'
        verbose_name_plural = 'Эскизы оформления'
        ordering = ['uploaded_at']

    def __str__(self):
        return f'Эскиз к позиции #{self.order_item_id} ({self.uploaded_at:%d.%m.%Y})'