document.addEventListener('DOMContentLoaded', () => {
    const burgerBtn = document.getElementById('burgerBtn');
    const mainNav = document.getElementById('mainNav');

    if (burgerBtn && mainNav) {
        burgerBtn.addEventListener('click', () => {
            const isOpen = mainNav.classList.toggle('is-open');
            burgerBtn.setAttribute('aria-expanded', String(isOpen));
        });
    }
});
