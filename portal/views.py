# portal/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q
from django.core.exceptions import FieldError

from reservas.models import Reserva, AreaReservavel
from financeiro.models import Lancamento
from comunicados.models import Aviso
from galeria.models import Evento  # eventos para o morador
from assembleias.models import Assembleia  # 👈 IMPORT
from condominios.models import Unidade     # 👈 IMPORT


def _condominio_do_morador(user):
    """Retorna o condomínio da unidade do morador (ou None)."""
    try:
        u = Unidade.objects.select_related("condominio").get(morador=user)
        return u.condominio
    except Unidade.DoesNotExist:
        return None


def _eventos_futuros(hoje, agora, limite=6):
    """
    Tenta diferentes campos comuns em Evento para obter os próximos eventos:
    - DateTimeField: data, quando, inicio
    - DateField: data
    Fallback: últimos cadastrados.
    """
    # 1) DateTimeField chamado "data"
    try:
        return Evento.objects.filter(data__gte=agora).order_by("data")[:limite]
    except Exception:
        pass

    # 2) DateField chamado "data"
    try:
        return Evento.objects.filter(data__gte=hoje).order_by("data")[:limite]
    except Exception:
        pass

    # 3) DateTimeField chamado "quando"
    try:
        return Evento.objects.filter(quando__gte=agora).order_by("quando")[:limite]
    except Exception:
        pass

    # 4) DateTimeField chamado "inicio"
    try:
        return Evento.objects.filter(inicio__gte=agora).order_by("inicio")[:limite]
    except Exception:
        pass

    # 5) Fallback: não quebra a página
    return Evento.objects.order_by("-id")[:limite]


@login_required
def home(request):
    """
    Dashboards por papel:
      - GESTOR: métricas de financeiro, 'Em uso agora', Próximas reservas, avisos.
      - PORTEIRO: agenda do dia.
      - MORADOR: minhas reservas (futuras/andamento), meus lançamentos, avisos, eventos e assembleias.
    """
    role = getattr(request.user, "role", "MORADOR")
    ctx = {}
    hoje = timezone.localdate()
    agora = timezone.localtime()

    # Avisos (comum)
    ctx["avisos"] = Aviso.objects.all()[:6]

    if role == "GESTOR":
        # Métricas de financeiro
        ctx["inadimplentes"] = Lancamento.objects.filter(
            pago_em__isnull=True, vencimento__lt=hoje
        ).count()
        ctx["pendentes"] = Lancamento.objects.filter(
            pago_em__isnull=True, vencimento__gte=hoje
        ).count()

        # Áreas (para ações rápidas)
        ctx["areas"] = AreaReservavel.objects.all()[:12]

        # Em uso agora: inicio <= agora < fim (exclui canceladas)
        ctx["em_uso_agora"] = (
            Reserva.objects.filter(inicio__lte=agora, fim__gt=agora)
            .exclude(status=Reserva.Status.CANCELADA)
            .select_related("morador", "area", "area__condominio")
            .order_by("fim")[:20]
        )

        # Próximas reservas: a partir de hoje (exceto as que estão em uso)
        ctx["reservas_proximas"] = (
            Reserva.objects.filter(inicio__date__gte=hoje)
            .exclude(status=Reserva.Status.CANCELADA)
            .exclude(inicio__lte=agora, fim__gt=agora)
            .select_related("morador", "area", "area__condominio")
            .order_by("inicio")[:20]
        )

        return render(request, "portal/dashboard_gestor.html", ctx)

    if role == "PORTEIRO":
        ctx["reservas_hoje"] = (
            Reserva.objects.filter(inicio__date=hoje)
            .exclude(status=Reserva.Status.CANCELADA)
            .select_related("morador", "area", "area__condominio")
            .order_by("inicio")
        )
        ctx["areas"] = AreaReservavel.objects.all()[:12]
        ctx["agora"] = agora
        return render(request, "portal/dashboard_porteiro.html", ctx)

    # MORADOR (default): só futuras/andamento (fim > agora)
    minhas = (
        Reserva.objects.filter(morador=request.user, fim__gt=agora)
        .exclude(status=Reserva.Status.CANCELADA)
        .select_related("area", "area__condominio")
        .order_by("inicio")[:10]
    )
    ctx["minhas_reservas"] = minhas

    # 🔒 Lançamentos visíveis ao morador:
    # - vinculados à unidade onde ele é morador
    # - OU direcionados diretamente (morador_alvo)
    # - OU incluído nos destinatários (M2M)
    ctx["meus_lancamentos"] = (
        Lancamento.objects.filter(
            Q(unidade__morador=request.user)
            | Q(morador_alvo=request.user)
            | Q(destinatarios=request.user)
        )
        .order_by("-vencimento")[:10]
    )

    # 👇 Eventos futuros (robusto para diferenças de schema)
    ctx["eventos"] = _eventos_futuros(hoje=hoje, agora=agora, limite=6)

    # 👇 Assembleias do condomínio do morador OU nas quais ele foi marcado
    cond = _condominio_do_morador(request.user)
    asm_qs = Assembleia.objects.filter(
        Q(condominio=cond) | Q(destinatarios=request.user)
    ).distinct()

    ctx["assembleias_proximas"] = asm_qs.filter(quando__gte=agora).order_by("quando")[:6]
    ctx["assembleias_passadas"] = asm_qs.filter(quando__lt=agora).order_by("-quando")[:6]

    ctx["agora"] = agora
    ctx["cancelaveis_ids"] = [r.id for r in minhas if r.inicio > agora]

    return render(request, "portal/dashboard_morador.html", ctx)