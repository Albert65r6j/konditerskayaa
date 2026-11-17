from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q

from orders.models import Order, validate_sketch_file_size





class Review(models.Model):

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='review',
        verbose_name='Выполненный заказ',
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор отзыва',
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Оценка (от 1 до 5)',
    )
    text = models.TextField(
        verbose_name='Текст отзыва',
    )
    result_photo = models.ImageField(
        upload_to='reviews/%Y/%m/',
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp']),
            validate_sketch_file_size,
        ],
        verbose_name='Фото готового торта',
    )
    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликован на сайте',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )

    class Meta:
        db_table = 'reviews_review'
        verbose_name = 'Отзыв покупателя'
        verbose_name_plural = 'Отзывы покупателей'
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(
                condition=Q(rating__gte=1) & Q(rating__lte=5),
                name='chk_review_rating_1_to_5',
            ),
        ]

    def __str__(self):
        return f'Отзыв на заказ №{self.order.order_number} — {self.rating}/5'
