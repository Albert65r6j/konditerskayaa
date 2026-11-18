document.addEventListener('DOMContentLoaded', () => {
    // 1. Мобильное меню-бургер
    const burgerBtn = document.getElementById('burgerBtn');
    const mainNav = document.getElementById('mainNav');
    if (burgerBtn && mainNav) {
        burgerBtn.addEventListener('click', () => {
            const isOpen = mainNav.classList.toggle('is-open');
            burgerBtn.setAttribute('aria-expanded', String(isOpen));
        });
    }

    // 2. Живой калькулятор конструктора + fetch-проверка квоты цеха
    const constructorForm = document.getElementById('constructorForm');
    if (constructorForm) {
        const spongeSelect = document.getElementById('spongeSelect');
        const fillingSelect = document.getElementById('fillingSelect');
        const weightInput = document.getElementById('weightInput');
        const decorCheckboxes = document.querySelectorAll('.decor-checkbox');
        const dateSelect = document.getElementById('dateSelect');
        const capacityStatus = document.getElementById('capacityStatus');

        const summaryWeight = document.getElementById('summaryWeight');
        const summaryBase = document.getElementById('summaryBase');
        const summaryDecor = document.getElementById('summaryDecor');
        const summaryTotal = document.getElementById('summaryTotal');

               function recalculatePrice() {
            const spongeOpt = spongeSelect ? spongeSelect.options[spongeSelect.selectedIndex] : null;
            const fillingOpt = fillingSelect ? fillingSelect.options[fillingSelect.selectedIndex] : null;
            const spongePrice = parseFloat(spongeOpt ? spongeOpt.dataset.price : 0) || 0;
            const fillingPrice = parseFloat(fillingOpt ? fillingOpt.dataset.price : 0) || 0;
            const weight = Math.max(1.5, Math.min(15, parseFloat(weightInput?.value || 2) || 2));

            let decorSum = 0;
            decorCheckboxes.forEach(cb => {
                if (cb.checked) decorSum += parseFloat(cb.dataset.price || 0) || 0;
            });

            const baseTotal = (spongePrice + fillingPrice) * weight;
            const grandTotal = baseTotal + decorSum;

            if (summaryWeight) summaryWeight.textContent = `${weight.toFixed(1)} кг`;
            if (summaryBase) summaryBase.textContent = `${Math.round(baseTotal).toLocaleString('ru-RU')} ₽`;
            if (summaryDecor) summaryDecor.textContent = `${Math.round(decorSum).toLocaleString('ru-RU')} ₽`;
            if (summaryTotal) summaryTotal.textContent = `${Math.round(grandTotal).toLocaleString('ru-RU')} ₽`;
        }

               async function checkShiftCapacity() {
            const baseUrl = constructorForm.dataset.capacityUrl;
            const dayId = dateSelect && dateSelect.value ? dateSelect.value : (dateSelect && dateSelect.options.length > 0 ? dateSelect.options[0].value : '');
            const weight = weightInput ? weightInput.value : '2.0';
            if (!baseUrl || !dayId || !capacityStatus) return;

            capacityStatus.textContent = 'Загрузка данных о смене...';
            capacityStatus.className = 'capacity-badge is-loading';

            try {
                const response = await fetch(`${baseUrl}?day_id=${encodeURIComponent(dayId)}&weight=${encodeURIComponent(weight)}`);
                if (!response.ok) throw new Error('Ошибка сети');
                const data = await response.json();
                capacityStatus.textContent = data.message;
                capacityStatus.className = data.is_enough ? 'capacity-badge is-ok' : 'capacity-badge is-warn';
            } catch (err) {
                capacityStatus.textContent = 'Не удалось проверить загрузку цеха.';
                capacityStatus.className = 'capacity-badge is-warn';
            }
        }


        [spongeSelect, fillingSelect, weightInput].forEach(el => {
            if (el) el.addEventListener('change', () => { recalculatePrice(); checkShiftCapacity(); });
            if (el) el.addEventListener('input', recalculatePrice);
        });
        decorCheckboxes.forEach(cb => cb.addEventListener('change', recalculatePrice));
        if (dateSelect) dateSelect.addEventListener('change', checkShiftCapacity);

        recalculatePrice();
        checkShiftCapacity();

        // 3. Клиентская валидация перед отправкой формы заказа
        constructorForm.addEventListener('submit', (e) => {
            clearClientErrors(constructorForm);
            let isValid = true;

            const weight = parseFloat(weightInput?.value || 0);
            if (isNaN(weight) || weight < 1.5 || weight > 15) {
                showClientError(weightInput, 'Укажите вес от 1.5 до 15.0 кг.');
                isValid = false;
            }

            const phoneInput = document.getElementById('phoneInput');
            const phoneDigits = (phoneInput?.value || '').replace(/\D/g, '');
            if (phoneDigits.length < 10) {
                showClientError(phoneInput, 'Введите корректный номер телефона (минимум 10 цифр).');
                isValid = false;
            }

            if (!isValid) e.preventDefault();
        });
    }

    // 4. Клиентская валидация формы регистрации
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', (e) => {
            clearClientErrors(registerForm);
            let isValid = true;
            const emailInput = registerForm.querySelector('input[type="email"]');
            const passInputs = registerForm.querySelectorAll('input[type="password"]');

            if (emailInput && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailInput.value.trim())) {
                showClientError(emailInput, 'Введите корректный адрес электронной почты.');
                isValid = false;
            }
            if (passInputs[0] && passInputs[0].value.length < 8) {
                showClientError(passInputs[0], 'Пароль должен содержать не менее 8 символов.');
                isValid = false;
            }
            if (passInputs[0] && passInputs[1] && passInputs[0].value !== passInputs[1].value) {
                showClientError(passInputs[1], 'Пароли не совпадают.');
                isValid = false;
            }
            if (!isValid) e.preventDefault();
        });
    }

    function showClientError(input, message) {
        if (!input) return;
        input.classList.add('is-invalid');
        const span = document.createElement('span');
        span.className = 'field-error client-error';
        span.textContent = message;
        input.parentNode.appendChild(span);
    }

    function clearClientErrors(form) {
        form.querySelectorAll('.client-error').forEach(el => el.remove());
        form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
    }
});
