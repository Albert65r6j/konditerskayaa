from decimal import Decimal
from django import forms
from django.db.models import F
from catalog.models import Decor, Filling, SpongeType
from production.models import ProductionDay


class OrderConstructorForm(forms.Form):
    sponge = forms.ModelChoiceField(
        queryset=SpongeType.objects.all(),
        label='Вид коржей',
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'spongeSelect'})
    )
    filling = forms.ModelChoiceField(
        queryset=Filling.objects.filter(is_active=True),
        label='Начинка',
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'fillingSelect'})
    )
    weight_kg = forms.DecimalField(
        label='Вес торта (кг)',
        min_value=Decimal('1.5'),
        max_value=Decimal('15.0'),
        decimal_places=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'id': 'weightInput', 'step': '0.5'})
    )
    inscription = forms.CharField(
        label='Надпись на торте',
        max_length=60,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'inscriptionInput', 'placeholder': 'До 60 символов'})
    )
    decors = forms.ModelMultipleChoiceField(
        queryset=Decor.objects.filter(is_active=True),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    sketch = forms.ImageField(
        label='Фото-эскиз (до 5 МБ)',
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'id': 'sketchInput', 'accept': '.jpg,.jpeg,.png,.webp'})
    )
    production_day = forms.ModelChoiceField(
        queryset=ProductionDay.objects.filter(booked_weight_kg__lt=F('max_weight_kg')).order_by('shift_date'),
        label='Дата производственной смены',
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'dateSelect'})
    )
    phone = forms.CharField(
        label='Контактный телефон',
        max_length=25,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'phoneInput', 'placeholder': '+7 (900) 123-45-67'})
    )
    delivery_address = forms.CharField(
        label='Адрес доставки или самовывоз',
        max_length=255,
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'id': 'addressInput', 'rows': 2, 'placeholder': 'Укажите адрес или напишите «Самовывоз»'})
    )

    def clean_sketch(self):
        file = self.cleaned_data.get('sketch')
        if file and file.size > 5 * 1024 * 1024:
            raise forms.ValidationError('Размер файла эскиза не должен превышать 5 МБ.')
        return file

    def clean(self):
        cleaned_data = super().clean()
        day = cleaned_data.get('production_day')
        weight = cleaned_data.get('weight_kg')
        if day and weight:
            remaining = day.max_weight_kg - day.booked_weight_kg
            if remaining < weight:
                self.add_error(
                    'production_day',
                    f'На выбранную дату свободно только {remaining} кг. Выберите другую смену или уменьшите вес.'
                )
        return cleaned_data
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        digits = ''.join(ch for ch in phone if ch.isdigit())
        if len(digits) < 10:
            raise forms.ValidationError('Введите корректный номер телефона (не менее 10 цифр).')
        return phone
