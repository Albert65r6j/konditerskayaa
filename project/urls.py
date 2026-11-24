from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.shortcuts import render

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('catalog.urls')),
    path('orders/', include('orders.urls')),
    path('accounts/', include('accounts.urls')),
    path('production/', include('production.urls')),
    path('reviews/', include('reviews.urls')),
    path('test-500/', trigger_error_500, name='test_500'),

]

#if settings.DEBUG:
    #import debug_toolbar
   # urlpatterns = [
       # path('__debug__/', include(debug_toolbar.urls)),
   # ] + urlpatterns

   

def custom_403(request, exception=None):
    return render(request, '403.html', status=403)

def custom_404(request, exception=None):
    return render(request, '404.html', status=404)

def custom_500(request):
    return render(request, '500.html', status=500)

def trigger_error_500(request):
    raise RuntimeError('Тестовая исключительная ситуация для проверки страницы 500')

handler403 = 'project.urls.custom_403'
handler404 = 'project.urls.custom_404'
handler500 = 'project.urls.custom_500'
