from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from catalog.models import BaseCake, Filling, SpongeType
from orders.models import Order
from production.models import ProductionDay

User = get_user_model()


class ExceptionHandlingNegativeTests(TestCase):
    def setUp(self):
        self.client = Client(SERVER_NAME='127.0.0.1')
        self.user = User.objects.create_user(username='client_test', password='StrongPassword123!')
        self.sponge = SpongeType.objects.create(name='Ванильный бисквит', extra_price_per_kg=Decimal('200.00'))
        self.filling = Filling.objects.create(name='Клубничный мусс', price_per_kg=Decimal('1500.00'), is_active=True)
        self.day = ProductionDay.objects.create(
            shift_date=date.today() + timedelta(days=3),
            pastry_chef=self.user,
            max_weight_kg=Decimal('10.0'),
            booked_weight_kg=Decimal('2.0'),
        )


    def test_1_nonexistent_cake_returns_404(self):
        """1. Обращение к несуществующей записи торта возвращает HTTP 404."""
        response = self.client.get(reverse('cake_detail', args=[999999]))
        self.assertEqual(response.status_code, 404)

    def test_2_unauthorized_schedule_access_returns_403(self):
        """2. Попытка доступа обычного пользователя к графику смен цеха возвращает HTTP 403."""
        self.client.login(username='client_test', password='StrongPassword123!')
        response = self.client.get('/production/schedule/')
        self.assertEqual(response.status_code, 403)


    def test_3_invalid_form_does_not_create_order_and_shows_message(self):
        """3. Отправка формы с неверными данными (вес < 1.5 кг, неверный телефон) не создаёт заказ."""
        self.client.login(username='client_test', password='StrongPassword123!')
        response = self.client.post(reverse('constructor'), {
            'sponge': self.sponge.id,
            'filling': self.filling.id,
            'weight_kg': '0.5',
            'production_day': self.day.id,
            'phone': '123',
            'delivery_address': 'Самовывоз',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Order.objects.count(), 0)
        self.assertContains(response, 'Минимальный вес торта составляет 1.5 кг.')

    def test_4_transaction_rollback_on_mid_operation_error(self):
        """4. При исключении в середине оформления заказа транзакция откатывается и данные не меняются."""
        self.client.login(username='client_test', password='StrongPassword123!')
        with patch('orders.views.OrderItem.calculate_price', side_effect=RuntimeError('Сбой расчёта')):
            response = self.client.post(reverse('constructor'), {
                'sponge': self.sponge.id,
                'filling': self.filling.id,
                'weight_kg': '3.0',
                'production_day': self.day.id,
                'phone': '+7 (900) 555-44-33',
                'delivery_address': 'Самовывоз',
            })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Order.objects.count(), 0)
        self.day.refresh_from_db()
        self.assertEqual(self.day.booked_weight_kg, Decimal('2.0'))

    def test_5_empty_queryset_calculation_does_not_crash(self):
        """5. Открытие каталога и поиск при пустой выборке тортов не вызывают ошибку деления на ноль."""
        BaseCake.objects.all().delete()
        response = self.client.get(reverse('catalog'), {'q': 'НесуществующийТорт'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Найдено позиций: 0')
