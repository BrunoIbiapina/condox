# financeiro/urls.py
from django.urls import path
from . import views

app_name = "financeiro"

urlpatterns = [
    path("meus/", views.minhas_cobrancas, name="minhas_cobrancas"),
]