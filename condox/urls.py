from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.urls import reverse_lazy

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('logout/', RedirectView.as_view(url=reverse_lazy('logout'), permanent=False)),
    path('', include('portal.urls', namespace='portal')),
    path('reservas/', include('reservas.urls', namespace='reservas')),
    path('eventos/', include('galeria.urls', namespace='galeria')),
    path('financeiro/', include('financeiro.urls', namespace='financeiro')),
    path("assembleias/", include(("assembleias.urls", "assembleias"), namespace="assembleias")),
]




if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)