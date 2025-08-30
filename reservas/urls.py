# reservas/urls.py
from django.urls import path
from . import views

app_name = 'reservas'

urlpatterns = [
    path('areas/', views.areas_list, name='areas_list'),
    path('areas/<int:area_id>/', views.area_detail, name='area_detail'),
    path('agendar/', views.agendar, name='agendar'),
    path('cancelar/<int:reserva_id>/', views.cancelar_reserva, name='cancelar_reserva'),
    path('historico/', views.historico, name='historico'),
]