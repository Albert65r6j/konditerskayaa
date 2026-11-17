from django.conf import settings
from django.db import models

def validate_sketch_file_size(value):
    max_size = 5 * 1024 * 1024  # 5 242 880 байт
    if value.size > max_size:
        raise ValidationError('Размер файла эскиза не должен превышать 5 МБ.')




class UserProfile(models.Model):

    class Role(models.TextChoices):
        CUSTOMER = 'customer', 'Покупатель'
        PASTRY_CHEF = 'pastry_chef', 'Кондитер'
        MANAGER = 'manager', 'Менеджер заказов'
        ADMIN = 'admin', 'Администратор'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Пользователь',
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER,
        verbose_name='Роль в системе',
    )
    phone = models.CharField(
        max_length=20,
        verbose_name='Контактный телефон',
        help_text='Формат: +7 (999) 123-45-67',
    )
    default_address = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Адрес доставки по умолчанию',
    )

    class Meta:
        db_table = 'accounts_userprofile'
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'
        ordering = ['user__username']

    def __str__(self):
        return f'{self.user.get_full_name() or self.user.username} ({self.get_role_display()})'

