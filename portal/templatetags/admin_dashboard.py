# portal/templatetags/admin_dashboard.py
from django import template
from django.utils import timezone
from django.db.models import Q
from reservas.models import Reserva
from financeiro.models import Lancamento

register = template.Library()


# ---------------- KPI tags ----------------
@register.simple_tag
def kpi_em_uso_agora():
    agora = timezone.localtime()
    return (
        Reserva.objects.filter(inicio__lte=agora, fim__gt=agora)
        .exclude(status=Reserva.Status.CANCELADA)
        .count()
    )


@register.simple_tag
def kpi_reservas_hoje():
    hoje = timezone.localdate()
    return (
        Reserva.objects.filter(inicio__date=hoje)
        .exclude(status=Reserva.Status.CANCELADA)
        .count()
    )


@register.simple_tag
def kpi_inadimplentes():
    hoje = timezone.localdate()
    return Lancamento.objects.filter(pago_em__isnull=True, vencimento__lt=hoje).count()


@register.simple_tag
def kpi_pendentes():
    hoje = timezone.localdate()
    return Lancamento.objects.filter(pago_em__isnull=True, vencimento__gte=hoje).count()


# --------------- Bloco detalhado ---------------
@register.inclusion_tag("admin/_stats_cards.html", takes_context=True)
def admin_stats_cards(context):
    """
    Retorna listas com poucos itens para aparecerem dentro de <details>.
    """
    agora = timezone.localtime()
    hoje = timezone.localdate()

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
        .order_by("vencimento")[:10]
    )

    pendentes = (
        Lancamento.objects.filter(pago_em__isnull=True, vencimento__gte=hoje)
        .select_related("unidade", "unidade__morador", "morador_alvo")
        .order_by("vencimento")[:10]
    )

    # helper para mostrar o nome do devedor
    def nome_do_morador(l):
        # prioridade: morador_alvo; depois morador da unidade; fallback “—”
        if getattr(l, "morador_alvo_id", None):
            return str(l.morador_alvo)
        if getattr(l, "unidade_id", None) and getattr(l.unidade, "morador_id", None):
            return str(l.unidade.morador)
        return "—"

    return {
        "em_uso": em_uso,
        "reservas_hoje": reservas_hoje,
        "inadimplentes": inadimplentes,
        "pendentes": pendentes,
        "nome_do_morador": nome_do_morador,
        "request": context.get("request"),
    }