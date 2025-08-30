# portal/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q

from reservas.models import Reserva, AreaReservavel
from financeiro.models import Lancamento
from comunicados.models import Aviso
from galeria.models import Evento
from assembleias.models import Assembleia
from condominios.models import Unidade


def _eventos_futuros(hoje, agora, limite=6):
    # Tenta diferentes campos comuns
    try:
        return Evento.objects.filter(data__gte=agora).order_by("data")[:limite]
    except Exception:
        pass
    try:
        return Evento.objects.filter(data__gte=hoje).order_by("data")[:limite]
    except Exception:
        pass
    try:
        return Evento.objects.filter(quando__gte=agora).order_by("quando")[:limite]
    except Exception:
        pass
    try:
        return Evento.objects.filter(inicio__gte=agora).order_by("inicio")[:limite]
    except Exception:
        pass
    return Evento.objects.order_by("-id")[:limite]


def _condominio_do_morador(user):
    try:
        unidade = Unidade.objects.select_related("condominio").get(morador=user)
        return unidade.condominio
    except Unidade.DoesNotExist:
        return None


@login_required
def home(request):
    """
    Dashboards por papel:
      - GESTOR: métricas/visões gerenciais
      - PORTEIRO: agenda do dia
      - MORADOR: minhas reservas, cobranças, avisos, eventos
    """
    role = getattr(request.user, "role", "MORADOR")
    ctx = {}
    hoje = timezone.localdate()
    agora = timezone.localtime()

    # Avisos (comum)
    ctx["avisos"] = Aviso.objects.all()[:6]

    if role == "GESTOR":
        ctx["inadimplentes"] = Lancamento.objects.filter(
            pago_em__isnull=True, vencimento__lt=hoje
        ).count()
        ctx["pendentes"] = Lancamento.objects.filter(
            pago_em__isnull=True, vencimento__gte=hoje
        ).count()
        ctx["areas"] = AreaReservavel.objects.all()[:12]
        ctx["em_uso_agora"] = (
            Reserva.objects.filter(inicio__lte=agora, fim__gt=agora)
            .exclude(status=Reserva.Status.CANCELADA)
            .select_related('morador', 'area', 'area__condominio')
            .order_by('fim')[:20]
        )
        ctx["reservas_proximas"] = (
            Reserva.objects.filter(inicio__date__gte=hoje)
            .exclude(status=Reserva.Status.CANCELADA)
            .exclude(inicio__lte=agora, fim__gt=agora)
            .select_related('morador', 'area', 'area__condominio')
            .order_by("inicio")[:20]
        )
        ctx["agora"] = agora
        return render(request, "portal/dashboard_gestor.html", ctx)

    if role == "PORTEIRO":
        ctx["reservas_hoje"] = (
            Reserva.objects.filter(inicio__date=hoje)
            .exclude(status=Reserva.Status.CANCELADA)
            .select_related('morador', 'area', 'area__condominio')
            .order_by("inicio")
        )
        ctx["areas"] = AreaReservavel.objects.all()[:12]
        ctx["agora"] = agora
        return render(request, "portal/dashboard_porteiro.html", ctx)

    # MORADOR
    minhas = (
        Reserva.objects.filter(morador=request.user, fim__gt=agora)
        .exclude(status=Reserva.Status.CANCELADA)
        .select_related("area", "area__condominio")
        .order_by("inicio")[:10]
    )
    ctx["minhas_reservas"] = minhas

    ctx["meus_lancamentos"] = (
        Lancamento.objects.filter(
            Q(unidade__morador=request.user)
            | Q(morador_alvo=request.user)
            | Q(destinatarios=request.user)
        )
        .order_by("-vencimento")[:10]
    )

    # Eventos e assembleias
    ctx["eventos"] = _eventos_futuros(hoje=hoje, agora=agora, limite=6)

    cond = _condominio_do_morador(request.user)
    if cond:
        proximas_asm = Assembleia.objects.filter(quando__gte=agora, condominio=cond)
    else:
        proximas_asm = Assembleia.objects.none()
    ctx["assembleias_proximas"] = proximas_asm.order_by("quando")[:6]

    ctx["agora"] = agora
    ctx["cancelaveis_ids"] = [r.id for r in minhas if r.inicio > agora]
    return render(request, "portal/dashboard_morador.html", ctx)