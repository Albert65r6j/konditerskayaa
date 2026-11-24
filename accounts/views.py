import logging
import time
from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
from accounts.forms import CustomLoginForm, RegisterForm
from accounts.models import UserProfile

logger = logging.getLogger('bakery.accounts')
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_SECONDS = 300


def register_view(request):
    if request.method == 'POST':
        logger.debug('Вход в обработку формы регистрации (POST /accounts/register/)')
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            UserProfile.objects.update_or_create(
                user=user,
                defaults={'phone': form.cleaned_data['phone'], 'role': 'CLIENT'}
            )
            login(request, user)
            logger.info('Зарегистрирован новый пользователь: %s', user.username)
            messages.success(request, f'Добро пожаловать, {user.first_name or user.username}! Регистрация завершена.')
            return redirect('home')
        logger.warning('Ошибка валидации при регистрации пользователя: %s', form.errors.as_json())
        messages.error(request, 'Пожалуйста, исправьте ошибки в форме регистрации.')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    lockout_until = request.session.get('login_lockout_until', 0)
    now = time.time()
    if lockout_until > now:
        remaining_sec = int(lockout_until - now)
        messages.error(
            request,
            f'Слишком много неудачных попыток входа. Повторите через {remaining_sec} сек.'
        )
        return render(request, 'accounts/login.html', {'form': CustomLoginForm()}, status=429)

    if request.method == 'POST':
        logger.debug('Вход в обработку формы авторизации (POST /accounts/login/)')
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            request.session['login_attempts'] = 0
            request.session.pop('login_lockout_until', None)
            user = form.get_user()
            login(request, user)
            logger.info('Успешный вход пользователя в систему: %s', user.username)
            messages.success(request, f'Вы успешно вошли как {user.username}.')
            return redirect('my_orders')

        attempts = request.session.get('login_attempts', 0) + 1
        request.session['login_attempts'] = attempts
        if attempts >= MAX_LOGIN_ATTEMPTS:
            request.session['login_lockout_until'] = now + LOCKOUT_SECONDS
            logger.warning('Блокировка входа на %s сек после %s неудачных попыток (логин: %s)', LOCKOUT_SECONDS, attempts, request.POST.get('username', '<пусто>'))
            messages.error(request, 'Превышен лимит попыток входа (5). Доступ временно заблокирован на 5 минут.')
            return render(request, 'accounts/login.html', {'form': form}, status=429)

        logger.warning('Неудачная попытка авторизации (%s/%s) для логина: %s', attempts, MAX_LOGIN_ATTEMPTS, request.POST.get('username', '<пусто>'))
        messages.error(request, f'Неверный логин или пароль. Осталось попыток: {MAX_LOGIN_ATTEMPTS - attempts}.')
    else:
        form = CustomLoginForm()
    return render(request, 'accounts/login.html', {'form': form})



def logout_view(request):
    logger.info('Выход пользователя из системы: %s', request.user)
    logout(request)
    messages.success(request, 'Вы вышли из учётной записи.')
    return redirect('home')
