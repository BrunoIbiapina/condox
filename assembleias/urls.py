# assembleias/urls.py
from django.urls import path
from . import views

app_name = "assembleias"

urlpatterns = [
    path("", views.lista, name="lista"),
    path("<int:pk>/", views.detalhe, name="detalhe"),
]