# financeiro/views.py
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.exceptions import PermissionDenied

from .models import Lancamento

@login_required
def minhas_cobrancas(request):
    """
    Lista todos os lançamentos visíveis para o morador logado:
      - Unidade onde ele é morador
      - OU direcionados diretamente (morador_alvo)
      - OU incluído em destinatarios (M2M)
    Suporta filtros por status e intervalo de datas (vencimento).
    """
    hoje = timezone.localdate()

    # Filtros (querystring)
    status = request.GET.get("status", "").upper().strip()  # PENDENTE | VENCIDO | PAGO | (vazio = todos)
    de_str = request.GET.get("de", "")
    ate_str = request.GET.get("ate", "")

    qs = Lancamento.objects.filter(
        Q(unidade__morador=request.user) |
        Q(morador_alvo=request.user) |
        Q(destinatarios=request.user)
    )

    # filtro por status
    if status == "PENDENTE":
        qs = qs.filter(pago_em__isnull=True, vencimento__gte=hoje)
    elif status == "VENCIDO":
        qs = qs.filter(pago_em__isnull=True, vencimento__lt=hoje)
    elif status == "PAGO":
        qs = qs.filter(pago_em__isnull=False)

    # filtro por data de vencimento (DateField → sem __date)
    try:
        if de_str:
            de = datetime.strptime(de_str, "%Y-%m-%d").date()
            qs = qs.filter(vencimento__gte=de)
    except Exception:
        de_str = ""
    try:
        if ate_str:
            ate = datetime.strptime(ate_str, "%Y-%m-%d").date()
            qs = qs.filter(vencimento__lte=ate)
    except Exception:
        ate_str = ""

    qs = qs.order_by("-vencimento", "-id")

    # paginação
    paginator = Paginator(qs, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    ctx = {
        "page_obj": page_obj,
        "status": status,
        "de": de_str,
        "ate": ate_str,
        "hoje": hoje,
    }
    return render(request, "financeiro/minhas_cobrancas.html", ctx)

@login_required
@require_POST
def enviar_comprovante(request, pk):
    """
    Upload do comprovante pelo morador, somente se o lançamento for visível a ele.
    """
    lanc = get_object_or_404(Lancamento, pk=pk)

    user = request.user
    autorizado = False
    if getattr(lanc, "morador_alvo_id", None) == user.id:
        autorizado = True
    elif getattr(lanc, "unidade_id", None) and getattr(lanc.unidade, "morador_id", None) == user.id:
        autorizado = True
    elif lanc.destinatarios.filter(pk=user.pk).exists():
        autorizado = True

    if not autorizado:
        raise PermissionDenied("Sem permissão para enviar comprovante deste lançamento.")

    file = request.FILES.get("comprovante_pdf")
    if not file:
        messages.error(request, "Selecione um arquivo.")
        return redirect(request.META.get("HTTP_REFERER", "/"))

    lanc.comprovante_pdf = file
    lanc.marcar_comprovante()
    lanc.save(update_fields=["comprovante_pdf", "comprovante_enviado_em"])
    messages.success(request, "Comprovante enviado! Aguarde conferência do gestor.")
    return redirect(request.META.get("HTTP_REFERER", "/"))