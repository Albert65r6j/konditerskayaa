from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
from accounts.forms import CustomLoginForm, RegisterForm
from accounts.models import UserProfile


def register_view(request):
    if request.method == 'POST':
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
            messages.success(request, f'Добро пожаловать, {user.first_name or user.username}! Регистрация завершена.')
            return redirect('home')
        messages.error(request, 'Пожалуйста, исправьте ошибки в форме регистрации.')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Вы успешно вошли как {user.username}.')
            return redirect('my_orders')
        messages.error(request, 'Неверный логин или пароль.')
    else:
        form = CustomLoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'Вы вышли из учётной записи.')
    return redirect('home')
