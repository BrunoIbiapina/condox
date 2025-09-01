from django.shortcuts import render, redirect
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
    """Tenta diferentes campos comuns para datas de Evento, evitando quebrar."""
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
def dashboard(request):
    """
    ÚNICO dashboard com o layout novo (portal/dashboard.html).
    A lógica aqui filtra os dados conforme o papel do usuário.
    """
    role = getattr(request.user, "role", "MORADOR")
    hoje = timezone.localdate()
    agora = timezone.localtime()

    # Flags para esconder/mostrar cards no template
    show_financeiro = show_avisos = show_eventos = show_assembleias = True

    # ---------- PORTEIRO: agenda do dia e uso agora (nada de financeiro) ----------
    if role == "PORTEIRO":
        show_financeiro = False
        cond = _condominio_do_morador(request.user)
        reservas_hoje = (
            Reserva.objects.filter(inicio__date=hoje)
            .exclude(status=Reserva.Status.CANCELADA)
            .select_related("area", "morador", "area__condominio")
            .order_by("inicio")
        )
        em_uso = (
            Reserva.objects.filter(inicio__lte=agora, fim__gt=agora)
            .exclude(status=Reserva.Status.CANCELADA)
            .select_related("area", "morador", "area__condominio")
            .order_by("fim")
        )
        # KPIs pontuais para os cards de cima
        kpi_em_uso_agora = em_uso.count()
        kpi_reservas_hoje = reservas_hoje.count()
        kpi_inadimplentes = 0
        kpi_pendentes = 0

        ctx = {
            "role": role,
            "agora": agora,
            "kpi_em_uso_agora": kpi_em_uso_agora,
            "kpi_reservas_hoje": kpi_reservas_hoje,
            "kpi_inadimplentes": kpi_inadimplentes,
            "kpi_pendentes": kpi_pendentes,
            "has_inadimplentes": False,

            "em_uso": em_uso[:8],
            "reservas_hoje": reservas_hoje[:10],

            "inadimplentes": [],  # escondido
            "pendentes": [],      # escondido

            "avisos": Aviso.objects.all()[:6],
            "eventos": _eventos_futuros(hoje, agora, limite=6),

            "assembleias_proximas": Assembleia.objects.filter(quando__gte=agora).order_by("quando")[:6],
            "has_asm_novas": Assembleia.objects.filter(quando__gte=agora, quando__lte=agora + timezone.timedelta(days=14)).exists(),

            "show_financeiro": show_financeiro,
            "show_avisos": show_avisos,
            "show_eventos": show_eventos,
            "show_assembleias": show_assembleias,
        }
        return render(request, "portal/dashboard.html", ctx)

    # ---------- MORADOR: dados apenas do próprio usuário ----------
    if role == "MORADOR":
        reservas_hoje = (
            Reserva.objects.filter(morador=request.user, inicio__date=hoje)
            .exclude(status=Reserva.Status.CANCELADA)
            .select_related("area", "area__condominio")
            .order_by("inicio")
        )
        em_uso = (
            Reserva.objects.filter(morador=request.user, inicio__lte=agora, fim__gt=agora)
            .exclude(status=Reserva.Status.CANCELADA)
            .select_related("area", "area__condominio")
            .order_by("fim")
        )
        # Financeiro só do próprio morador
        base_fin = Q(unidade__morador=request.user) | Q(morador_alvo=request.user) | Q(destinatarios=request.user)
        inadimplentes = Lancamento.objects.filter(base_fin, pago_em__isnull=True, vencimento__lt=hoje).order_by("vencimento")[:6]
        pendentes     = Lancamento.objects.filter(base_fin, pago_em__isnull=True, vencimento__gte=hoje).order_by("vencimento")[:6]

        cond = _condominio_do_morador(request.user)
        asm_qs = Assembleia.objects.filter(quando__gte=agora)
        if cond:
            asm_qs = asm_qs.filter(condominio=cond)

        ctx = {
            "role": role,
            "agora": agora,
            "kpi_em_uso_agora": em_uso.count(),
            "kpi_reservas_hoje": reservas_hoje.count(),
            "kpi_inadimplentes": inadimplentes.count(),
            "kpi_pendentes": pendentes.count(),
            "has_inadimplentes": inadimplentes.exists(),

            "em_uso": em_uso[:8],
            "reservas_hoje": reservas_hoje[:10],
            "inadimplentes": inadimplentes,
            "pendentes": pendentes,

            "avisos": Aviso.objects.all()[:6],
            "eventos": _eventos_futuros(hoje, agora, limite=6),

            "assembleias_proximas": asm_qs.order_by("quando")[:6],
            "has_asm_novas": asm_qs.filter(quando__lte=agora + timezone.timedelta(days=14)).exists(),

            "show_financeiro": show_financeiro,
            "show_avisos": show_avisos,
            "show_eventos": show_eventos,
            "show_assembleias": show_assembleias,
        }
        return render(request, "portal/dashboard.html", ctx)

    # ---------- GESTOR: visão geral do condomínio ----------
    # KPIs gerais
    kpi_em_uso_agora = (
        Reserva.objects.filter(inicio__lte=agora, fim__gt=agora)
        .exclude(status=Reserva.Status.CANCELADA)
        .count()
    )
    kpi_reservas_hoje = (
        Reserva.objects.filter(inicio__date=hoje)
        .exclude(status=Reserva.Status.CANCELADA)
        .count()
    )
    kpi_inadimplentes = Lancamento.objects.filter(pago_em__isnull=True, vencimento__lt=hoje).count()
    kpi_pendentes = Lancamento.objects.filter(pago_em__isnull=True, vencimento__gte=hoje).count()

    em_uso = (
        Reserva.objects.filter(inicio__lte=agora, fim__gt=agora)
        .exclude(status=Reserva.Status.CANCELADA)
        .select_related("area", "morador", "area__condominio")
        .order_by("fim")[:8]
    )
    reservas_hoje = (
        Reserva.objects.filter(inicio__date=hoje)
        .exclude(status=Reserva.Status.CANCELADA)
        .select_related("area", "morador", "area__condominio")
        .order_by("inicio")[:10]
    )
    inadimplentes = (
        Lancamento.objects.filter(pago_em__isnull=True, vencimento__lt=hoje)
        .select_related("unidade", "unidade__morador", "morador_alvo")
        .order_by("vencimento")[:6]
    )
    pendentes = (
        Lancamento.objects.filter(pago_em__isnull=True, vencimento__gte=hoje)
        .select_related("unidade", "unidade__morador", "morador_alvo")
        .order_by("vencimento")[:6]
    )

    ctx = {
        "role": role,
        "agora": agora,
        "kpi_em_uso_agora": kpi_em_uso_agora,
        "kpi_reservas_hoje": kpi_reservas_hoje,
        "kpi_inadimplentes": kpi_inadimplentes,
        "kpi_pendentes": kpi_pendentes,
        "has_inadimplentes": kpi_inadimplentes > 0,

        "em_uso": em_uso,
        "reservas_hoje": reservas_hoje,
        "inadimplentes": inadimplentes,
        "pendentes": pendentes,

        "avisos": Aviso.objects.all()[:6],
        "eventos": _eventos_futuros(hoje, agora, limite=6),
        "assembleias_proximas": Assembleia.objects.filter(quando__gte=agora).order_by("quando")[:6],
        "has_asm_novas": Assembleia.objects.filter(quando__gte=agora, quando__lte=agora + timezone.timedelta(days=14)).exists(),

        "show_financeiro": show_financeiro,
        "show_avisos": show_avisos,
        "show_eventos": show_eventos,
        "show_assembleias": show_assembleias,
    }
    return render(request, "portal/dashboard.html", ctx)


@login_required
def home(request):
    """Mantido por compatibilidade — envia para o dashboard novo."""
    return redirect("dashboard")