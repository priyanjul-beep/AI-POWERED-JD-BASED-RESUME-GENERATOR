from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.authentication.urls')),
    path('api/profile/', include('apps.profiles.urls')),
    path('api/documents/', include('apps.documents.urls')),
    path('api/resume-generations/', include('apps.generations.urls')),
    path('api/resume-history/', include('apps.history.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
