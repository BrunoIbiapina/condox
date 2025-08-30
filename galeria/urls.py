from django.urls import path
from . import views

# Define um namespace para evitar conflito de nomes em outros apps
app_name = "galeria"

urlpatterns = [
    # Lista de eventos
    path("", views.lista_eventos, name="lista"),

    # Detalhe de um evento específico (pela PK)
    path("<int:pk>/", views.detalhe_evento, name="detalhe"),
]