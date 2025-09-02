# condox/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from portal import views as portal_views

urlpatterns = [
    path("admin/", admin.site.urls),

    # LOGIN/LOGOUT (se já usa auth padrão)
    path("accounts/", include("django.contrib.auth.urls")),

    # >>> Home única que escolhe o dashboard por papel <<<
    path("", portal_views.home, name="home"),

    # apps
    path("portal/", include(("portal.urls", "portal"), namespace="portal")),
    path("reservas/", include(("reservas.urls", "reservas"), namespace="reservas")),
    path("eventos/", include(("galeria.urls", "galeria"), namespace="galeria")),
    path("financeiro/", include(("financeiro.urls", "financeiro"), namespace="financeiro")),
    path("assembleias/", include(("assembleias.urls", "assembleias"), namespace="assembleias")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)