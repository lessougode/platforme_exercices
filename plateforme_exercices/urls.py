from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cours/', include('cours.urls')),
    path('exercices/', include('exercices.urls')),
    path('devoirs/', include('devoirs.urls')),
    path('gestion/', include('rapports.urls')),
    path('', include('comptes.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
