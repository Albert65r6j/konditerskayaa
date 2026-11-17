from decimal import Decimal
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q



class Filling(models.Model):

    name = models.CharField(
        max_length=120,
        unique=True,
        verbose_name='Название начинки',
    )
    description = models.TextField(
        verbose_name='Состав и аллергены',
    )
    price_per_kg = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('100.00'))],
        verbose_name='Цена за 1 кг (руб.)',
    )
    calories_per_100g = models.PositiveSmallIntegerField(
        default=320,
        verbose_name='Калорийность (ккал / 100 г)',
    )
    cut_photo = models.ImageField(
        upload_to='fillings/',
        blank=True,
        null=True,
        verbose_name='Фото разреза',
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Доступна для заказа',
    )

    class Meta:
        db_table = 'catalog_filling'
        verbose_name = 'Начинка'
        verbose_name_plural = 'Начинки'
        ordering = ['name']
        constraints = [
            models.CheckConstraint(
                condition=Q(price_per_kg__gt=0),
                name='chk_filling_price_positive',
            ),
        ]

    def __str__(self):
        return f'{self.name} ({self.price_per_kg} руб./кг)'


class SpongeType(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Вид коржа',
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание текстуры и состава',
    )
    extra_price_per_kg = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Доплата за 1 кг (руб.)',
    )
    is_gluten_free = models.BooleanField(
        default=False,
        verbose_name='Без глютена',
    )

    class Meta:
        db_table = 'catalog_spongetype'
        verbose_name = 'Вид коржа'
        verbose_name_plural = 'Виды коржей'
        ordering = ['name']
        constraints = [
            models.CheckConstraint(
                condition=Q(extra_price_per_kg__gte=0),
                name='chk_spongetype_extra_non_negative',
            ),
        ]

    def __str__(self):
        if self.extra_price_per_kg > 0:
            return f'{self.name} (+{self.extra_price_per_kg} руб./кг)'
        return self.name


class BaseCake(models.Model):

    class Category(models.TextChoices):
        KIDS = 'kids', 'Детские торты'
        WEDDING = 'wedding', 'Свадебные торты'
        BENTO = 'bento', 'Бенто-торты'
        HOLIDAY = 'holiday', 'Праздничные и юбилейные'
        CORPORATE = 'corporate', 'Корпоративные'

    title = models.CharField(
        max_length=150,
        verbose_name='Название базового торта',
    )
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.HOLIDAY,
        verbose_name='Категория повода',
    )
    description = models.TextField(
        verbose_name='Описание вкуса и оформления',
    )
    min_weight_kg = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=Decimal('1.50'),
        validators=[MinValueValidator(Decimal('0.40')), MaxValueValidator(Decimal('25.00'))],
        verbose_name='Минимальный вес (кг)',
    )
    default_filling = models.ForeignKey(
        Filling,
        on_delete=models.PROTECT,
        related_name='base_cakes',
        verbose_name='Базовая начинка',
    )
    default_sponge = models.ForeignKey(
        SpongeType,
        on_delete=models.PROTECT,
        related_name='base_cakes',
        verbose_name='Базовый вид коржа',
    )
    photo = models.ImageField(
        upload_to='cakes/',
        blank=True,
        null=True,
        verbose_name='Фотография торта',
    )
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('5.00'),
        validators=[MinValueValidator(Decimal('1.00')), MaxValueValidator(Decimal('5.00'))],
        verbose_name='Средний рейтинг',
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Отображать в каталоге',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления',
    )

    class Meta:
        db_table = 'catalog_basecake'
        verbose_name = 'Базовый торт'
        verbose_name_plural = 'Базовые торты'
        ordering = ['-created_at', 'title']
        constraints = [
            models.CheckConstraint(
                condition=Q(min_weight_kg__gte=Decimal('0.40')),
                name='chk_basecake_min_weight',
            ),
        ]

    def __str__(self):
        return f'{self.title} (от {self.min_weight_kg} кг)'


class Decor(models.Model):

    class Complexity(models.TextChoices):
        BASIC = 'basic', 'Базовый декор'
        COMPLEX = 'complex', 'Сложный авторский декор'

    name = models.CharField(
        max_length=120,
        unique=True,
        verbose_name='Название элемента декора',
    )
    complexity = models.CharField(
        max_length=15,
        choices=Complexity.choices,
        default=Complexity.BASIC,
        verbose_name='Уровень сложности',
    )
    surcharge = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Фиксированная надбавка (руб.)',
    )
    prep_hours = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=Decimal('0.5'),
        verbose_name='Время на изготовление (ч)',
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Доступен для выбора',
    )

    class Meta:
        db_table = 'catalog_decor'
        verbose_name = 'Элемент декора'
        verbose_name_plural = 'Элементы декора'
        ordering = ['complexity', 'name']
        constraints = [
            models.CheckConstraint(
                condition=Q(surcharge__gte=0),
                name='chk_decor_surcharge_non_negative',
            ),
        ]

    def __str__(self):
        return f'{self.name} (+{self.surcharge} руб.)'