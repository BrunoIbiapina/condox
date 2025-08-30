# galeria/views.py
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.core.exceptions import FieldError

from .models import Evento


def lista_eventos(request):
    """
    Lista eventos futuros (a partir de hoje).
    Funciona com Evento.data sendo DateField ou DateTimeField.
    """
    hoje = timezone.localdate()
    agora = timezone.localtime()

    # Tenta filtrar por data >= hoje/now conforme o tipo do campo
    try:
        # Se for DateTimeField, comparar com "agora" funciona
        eventos = Evento.objects.filter(data__gte=agora).order_by("data")[:50]
        if not eventos.exists():
            # fallback: se o campo for DateField, tenta com a data de hoje
            eventos = Evento.objects.filter(data__gte=hoje).order_by("data")[:50]
    except FieldError:
        # Se "data" for DateField
        eventos = Evento.objects.filter(data__gte=hoje).order_by("data")[:50]

    return render(request, "galeria/lista_eventos.html", {"eventos": eventos})


def detalhe_evento(request, pk: int):
    """
    Detalhe de um evento específico.
    """
    evento = get_object_or_404(Evento, pk=pk)
    return render(request, "galeria/detalhe_evento.html", {"evento": evento})