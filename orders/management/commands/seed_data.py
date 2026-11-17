import random
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import UserProfile
from catalog.models import BaseCake, Decor, Filling, SpongeType
from orders.models import Order, OrderItem, OrderItemDecor
from production.models import ProductionDay
from reviews.models import Review

User = get_user_model()


class Command(BaseCommand):
    help = 'Заполняет БД кондитерской демонстрационными данными (35+ заказов и справочники).'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('Начинаем генерацию демонстрационных данных ИС «Кондитерская»...')


        admin_user, _ = User.objects.get_or_create(
            username='admin_bakery',
            defaults={
                'email': 'admin@sweetcraft.ru',
                'first_name': 'Елена',
                'last_name': 'Соколова',
                'is_staff': True,
                'is_superuser': True,
            },
        )
        admin_user.set_password('AdminPass123!')
        admin_user.save()
        UserProfile.objects.update_or_create(
            user=admin_user,
            defaults={'role': UserProfile.Role.ADMIN, 'phone': '+7 (900) 100-00-01'},
        )

        managers = []
        for idx, (uname, fname, lname) in enumerate([
            ('manager_anna', 'Анна', 'Морозова'),
            ('manager_olga', 'Ольга', 'Волкова'),
        ], start=1):
            u, _ = User.objects.get_or_create(
                username=uname,
                defaults={
                    'email': f'{uname}@sweetcraft.ru',
                    'first_name': fname,
                    'last_name': lname,
                    'is_staff': True,
                },
            )
            u.set_password('ManagerPass123!')
            u.save()
            UserProfile.objects.update_or_create(
                user=u,
                defaults={'role': UserProfile.Role.MANAGER, 'phone': f'+7 (900) 200-00-0{idx}'},
            )
            managers.append(u)

        chefs = []
        for idx, (uname, fname, lname) in enumerate([
            ('chef_dmitry', 'Дмитрий', 'Ковалёв'),
            ('chef_marina', 'Марина', 'Лебедева'),
            ('chef_irina', 'Ирина', 'Новикова'),
        ], start=1):
            u, _ = User.objects.get_or_create(
                username=uname,
                defaults={
                    'email': f'{uname}@sweetcraft.ru',
                    'first_name': fname,
                    'last_name': lname,
                },
            )
            u.set_password('ChefPass123!')
            u.save()
            UserProfile.objects.update_or_create(
                user=u,
                defaults={'role': UserProfile.Role.PASTRY_CHEF, 'phone': f'+7 (900) 300-00-0{idx}'},
            )
            chefs.append(u)

        customers = []
        customer_names = [
            ('client_ivan', 'Иван', 'Петров'),
            ('client_maria', 'Мария', 'Смирнова'),
            ('client_alex', 'Алексей', 'Кузнецов'),
            ('client_kate', 'Екатерина', 'Попова'),
            ('client_sergey', 'Сергей', 'Васильев'),
            ('client_natalia', 'Наталья', 'Фёдорова'),
            ('client_pavel', 'Павел', 'Михайлов'),
            ('client_svetlana', 'Светлана', 'Андреева'),
            ('client_roman', 'Роман', 'Алексеев'),
            ('client_julia', 'Юлия', 'Романова'),
            ('client_denis', 'Денис', 'Захаров'),
            ('client_tatiana', 'Татьяна', 'Белова'),
        ]
        for idx, (uname, fname, lname) in enumerate(customer_names, start=1):
            u, _ = User.objects.get_or_create(
                username=uname,
                defaults={
                    'email': f'{uname}@example.ru',
                    'first_name': fname,
                    'last_name': lname,
                },
            )
            u.set_password('ClientPass123!')
            u.save()
            UserProfile.objects.update_or_create(
                user=u,
                defaults={
                    'role': UserProfile.Role.CUSTOMER,
                    'phone': f'+7 (917) 555-{idx:02d}-{idx:02d}',
                    'default_address': f'г. Ульяновск, ул. Гончарова, д. {idx * 3}, кв. {idx * 5}',
                },
            )
            customers.append(u)

        fillings_data = [
            ('Фисташка-малина', 'Фисташковый мусс на белом шоколаде, малиновое конфи, крем-чиз.', Decimal('2300.00'), 340),
            ('Три шоколада', 'Муссы из горького, молочного и белого бельгийского шоколада.', Decimal('2150.00'), 390),
            ('Манго-маракуйя', 'Тропическое пюре манго и маракуйи с нежным сливочным муссом.', Decimal('2200.00'), 295),
            ('Красный бархат с вишней', 'Крем-чиз на сливках и пряная вишнёвая прослойка.', Decimal('1950.00'), 355),
            ('Сникерс карамельный', 'Домашняя солёная карамель, жареный арахис и шоколадный ганаш.', Decimal('2100.00'), 420),
            ('Медовик классический', 'Тонкие медовые коржи со сметанно-сливочным кремом.', Decimal('1750.00'), 360),
            ('Наполеон заварной', 'Хрустящие слоёные коржи с ванильным заварным кремом пломбир.', Decimal('1800.00'), 385),
            ('Молочная девочка', 'Коржи на сгущённом молоке с кремом дипломат и свежей клубникой.', Decimal('1900.00'), 330),
            ('Чёрный лес (Шварцвальд)', 'Шоколадный крем, вишня в собственном соку и взбитые сливки.', Decimal('2000.00'), 345),
            ('Рафаэлло кокосовый', 'Кокосовый крем на маскарпоне, хрустящий миндаль и вафельная крошка.', Decimal('2150.00'), 405),
            ('Груша-горгонзола', 'Авторская начинка с карамелизированной грушей и сыром с голубой плесенью.', Decimal('2450.00'), 350),
            ('Клубничный йогурт', 'Лёгкий йогуртовый мусс с кусочками садовой клубники (низкокалорийный).', Decimal('1850.00'), 250),
        ]
        fillings = []
        for name, desc, price, kcal in fillings_data:
            obj, _ = Filling.objects.update_or_create(
                name=name,
                defaults={'description': desc, 'price_per_kg': price, 'calories_per_100g': kcal},
            )
            fillings.append(obj)


        sponges_data = [
            ('Ванильный шифоновый бисквит', 'Воздушный бисквит с натуральной бурбонской ванилью.', Decimal('0.00'), False),
            ('Шоколадный брауни-бисквит', 'Влажный насыщенный бисквит на тёмном какао.', Decimal('100.00'), False),
            ('Красный бархат', 'Бархатистый бисквит с лёгкой шоколадной ноткой.', Decimal('100.00'), False),
            ('Медовые коржи', 'Ароматные тонкие коржи на цветочном мёде.', Decimal('50.00'), False),
            ('Слоёные коржи', 'Классическое рубленое слоёное тесто.', Decimal('50.00'), False),
            ('Миндальный дакуаз', 'Ореховый безглютеновый корж на миндальной муке.', Decimal('250.00'), True),
            ('Фисташковый бисквит', 'Бисквит с добавлением натуральной фисташковой пасты.', Decimal('200.00'), False),
            ('Морковно-пряный бисквит', 'С грецким орехом, корицей и цедрой апельсина.', Decimal('150.00'), False),
            ('Безглютеновый рисовый бисквит', 'Лёгкий бисквит на рисовой и кукурузной муке.', Decimal('200.00'), True),
            ('Маковый бисквит', 'Классический бисквит с обжаренным кондитерским маком.', Decimal('100.00'), False),
        ]
        sponges = []
        for name, desc, extra, gf in sponges_data:
            obj, _ = SpongeType.objects.update_or_create(
                name=name,
                defaults={'description': desc, 'extra_price_per_kg': extra, 'is_gluten_free': gf},
            )
            sponges.append(obj)

        decors_data = [
            ('Базовое выравнивание крем-чизом', Decor.Complexity.BASIC, Decimal('0.00'), Decimal('0.5')),
            ('Поздравительная надпись кремом', Decor.Complexity.BASIC, Decimal('200.00'), Decimal('0.3')),
            ('Шоколадные подтёки', Decor.Complexity.BASIC, Decimal('350.00'), Decimal('0.5')),
            ('Ягодный венок (свежая малина и голубика)', Decor.Complexity.BASIC, Decimal('750.00'), Decimal('0.8')),
            ('Акриловый топпер с надписью', Decor.Complexity.BASIC, Decimal('450.00'), Decimal('0.2')),
            ('Съедобная фотопечать на сахарной бумаге', Decor.Complexity.COMPLEX, Decimal('850.00'), Decimal('1.0')),
            ('Ручная лепка фигурки из мастики', Decor.Complexity.COMPLEX, Decimal('1500.00'), Decimal('2.5')),
            ('Шоколадные сферы и темперированный декор', Decor.Complexity.COMPLEX, Decimal('1100.00'), Decimal('1.5')),
            ('Велюровое покрытие (какао-масло)', Decor.Complexity.COMPLEX, Decimal('900.00'), Decimal('1.0')),
            ('Живые цветы с изоляцией стеблей', Decor.Complexity.COMPLEX, Decimal('1200.00'), Decimal('1.2')),
        ]
        decors = []
        for name, comp, surcharge, hours in decors_data:
            obj, _ = Decor.objects.update_or_create(
                name=name,
                defaults={'complexity': comp, 'surcharge': surcharge, 'prep_hours': hours},
            )
            decors.append(obj)

        categories = [
            BaseCake.Category.KIDS,
            BaseCake.Category.WEDDING,
            BaseCake.Category.BENTO,
            BaseCake.Category.HOLIDAY,
            BaseCake.Category.CORPORATE,
        ]
        base_cakes = []
        for i in range(1, 31):
            cat = categories[(i - 1) % len(categories)]
            min_w = Decimal('0.50') if cat == BaseCake.Category.BENTO else Decimal('2.00')
            cake, _ = BaseCake.objects.update_or_create(
                title=f'Авторский торт №{i} «{fillings[(i - 1) % len(fillings)].name}»',
                defaults={
                    'category': cat,
                    'description': f'Фирменный дизайн №{i} для категории «{cat.label}». Идеальный баланс вкуса.',
                    'min_weight_kg': min_w,
                    'default_filling': fillings[(i - 1) % len(fillings)],
                    'default_sponge': sponges[(i - 1) % len(sponges)],
                    'rating': Decimal(str(round(random.uniform(4.6, 5.0), 2))),
                    'is_active': True,
                },
            )
            base_cakes.append(cake)

        today = date(2026, 11, 14)
        shifts = []
        for offset in range(-7, 7):
            s_date = today + timedelta(days=offset)
            shift, _ = ProductionDay.objects.update_or_create(
                shift_date=s_date,
                defaults={
                    'pastry_chef': chefs[abs(offset) % len(chefs)],
                    'max_weight_kg': Decimal('25.00'),
                    'booked_weight_kg': Decimal('0.00'),
                    'notes': 'Плановая смена кондитерского цеха',
                },
            )
            shifts.append(shift)


        statuses_pool = [
            Order.Status.COMPLETED,
            Order.Status.READY,
            Order.Status.IN_PROGRESS,
            Order.Status.PREPAID,
            Order.Status.NEW,
        ]
        created_orders = []
        for idx in range(1, 36):
            shift = shifts[(idx - 1) % len(shifts)]
            customer = customers[(idx - 1) % len(customers)]
            filling = fillings[(idx * 2) % len(fillings)]
            sponge = sponges[idx % len(sponges)]
            weight = Decimal(str(random.choice([1.5, 2.0, 2.5, 3.0, 3.5])))

            if shift.booked_weight_kg + weight > shift.max_weight_kg:
                weight = Decimal('1.00')

            status = (
                Order.Status.COMPLETED
                if shift.shift_date < today
                else statuses_pool[idx % len(statuses_pool)]
            )

            order, _ = Order.objects.get_or_create(
                order_number=f'ORD-2026-{idx:04d}',
                defaults={
                    'customer': customer,
                    'production_day': shift,
                    'delivery_interval': random.choice(['10:00–13:00', '13:00–16:00', '16:00–19:00']),
                    'delivery_type': Order.DeliveryType.COURIER if idx % 2 == 0 else Order.DeliveryType.PICKUP,
                    'delivery_address': customer.profile.default_address if idx % 2 == 0 else '',
                    'status': status,
                },
            )


            order.items.all().delete()

            item = OrderItem.objects.create(
                order=order,
                base_cake=base_cakes[idx % len(base_cakes)] if idx % 3 != 0 else None,
                filling=filling,
                sponge_type=sponge,
                weight_kg=weight,
                inscription_text='С Днём Рождения!' if idx % 2 == 0 else '',
            )


            chosen_decors = random.sample(decors, k=2 if idx % 2 == 0 else 1)
            for d in chosen_decors:
                OrderItemDecor.objects.create(
                    order_item=item,
                    decor=d,
                    applied_surcharge=d.surcharge,
                    custom_note='Согласовано в конструкторе',
                )

            item.item_price = item.calculate_price()
            item.save(update_fields=['item_price'])

            order.total_weight_kg = weight
            order.total_price = item.item_price
            order.prepayment_amount = (
                (item.item_price * Decimal('0.50')).quantize(Decimal('0.01'))
                if status != Order.Status.NEW
                else Decimal('0.00')
            )
            order.save(update_fields=['total_weight_kg', 'total_price', 'prepayment_amount'])

            if status != Order.Status.CANCELLED:
                shift.booked_weight_kg += weight
                shift.save(update_fields=['booked_weight_kg'])

            created_orders.append(order)


        completed_orders = [o for o in created_orders if o.status == Order.Status.COMPLETED][:15]
        for idx, order in enumerate(completed_orders, start=1):
            Review.objects.update_or_create(
                order=order,
                defaults={
                    'author': order.customer,
                    'rating': 5 if idx % 4 != 0 else 4,
                    'text': f'Заказывали торт №{order.order_number}. Начинка свежая, доставили точно в интервал!',
                    'is_published': True,
                },
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'Готово! Создано: начинок={Filling.objects.count()}, коржей={SpongeType.objects.count()}, '
                f'декора={Decor.objects.count()}, базовых тортов={BaseCake.objects.count()}, '
                f'смен={ProductionDay.objects.count()}, заказов={Order.objects.count()}, '
                f'отзывов={Review.objects.count()}.'
            )
        )
