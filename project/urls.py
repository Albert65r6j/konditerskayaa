from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('catalog.urls')),
    path('orders/', include('orders.urls')),
    path('accounts/', include('accounts.urls')),
    path('production/', include('production.urls')),
    path('reviews/', include('reviews.urls')),
]

#if settings.DEBUG:
    #import debug_toolbar
   # urlpatterns = [
       # path('__debug__/', include(debug_toolbar.urls)),
   # ] + urlpatterns