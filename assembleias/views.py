# assembleias/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.utils import timezone

from .models import Assembleia
from condominios.models import Unidade


def _condominio_do_morador(user):
    """
    Retorna o condomínio da unidade em que o usuário é morador.
    Ajuste aqui se sua relação for diferente (ex.: user.unidade.condominio).
    """
    if not user.is_authenticated:
        return None
    try:
        unidade = (
            Unidade.objects
            .select_related("condominio")
            .get(morador=user)
        )
        return unidade.condominio
    except Unidade.DoesNotExist:
        return None


@login_required
def lista(request):
    """
    Morador vê:
      - Assembleias do seu condomínio
      - OU assembleias nas quais ele foi explicitamente marcado em 'destinatarios'
    Gestor/Staff: vê tudo (ajuste se quiser limitar por condomínio do gestor).
    """
    user = request.user
    agora = timezone.now()

    if getattr(user, "role", "") == "GESTOR" or user.is_staff:
        qs = Assembleia.objects.all()
    else:
        cond = _condominio_do_morador(user)
        # Se o morador não tem unidade vinculada a um condomínio,
        # mostramos apenas assembleias onde ele foi marcado como destinatário.
        base_filter = Q(destinatarios=user)
        if cond is not None:
            base_filter = Q(condominio=cond) | base_filter

        qs = Assembleia.objects.filter(base_filter).distinct()

    # Pré-carregamentos leves para template (evita N+1 em muitos destinatários)
    qs = qs.select_related("condominio").prefetch_related("destinatarios")

    proximas = qs.filter(quando__gte=agora).order_by("quando")
    passadas = qs.filter(quando__lt=agora).order_by("-quando")

    context = {
        "proximas": proximas,
        "passadas": passadas,
    }
    return render(request, "assembleias/lista.html", context)


@login_required
def detalhe(request, pk: int):
    """
    Página de detalhe com anexos (convocação/ata) e informações.
    Aplica a mesma regra de visibilidade da listagem.
    """
    asm = get_object_or_404(
        Assembleia.objects.select_related("condominio").prefetch_related("destinatarios"),
        pk=pk,
    )

    user = request.user
    if getattr(user, "role", "") == "GESTOR" or user.is_staff:
        autorizado = True
    else:
        cond = _condominio_do_morador(user)
        autorizado = (
            (cond is not None and asm.condominio_id == getattr(cond, "id", None))
            or asm.destinatarios.filter(pk=user.pk).exists()
        )

    if not autorizado:
        # Usamos 404 para não revelar a existência do recurso
        from django.http import Http404
        raise Http404("Assembleia não encontrada")

    return render(request, "assembleias/detalhe.html", {"a": asm})