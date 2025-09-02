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

@login_required
def home(request):
    role = getattr(request.user, "role", "MORADOR")  # MORADOR por padrão
    hoje = timezone.localdate()
    agora = timezone.localtime()

    if role == "GESTOR":
        ctx = {
            "inadimplentes": Lancamento.objects.filter(pago_em__isnull=True, vencimento__lt=hoje).count(),
            "pendentes": Lancamento.objects.filter(pago_em__isnull=True, vencimento__gte=hoje).count(),
            "areas": AreaReservavel.objects.all()[:12],
            "em_uso_agora": (
                Reserva.objects.filter(inicio__lte=agora, fim__gt=agora)
                .exclude(status=Reserva.Status.CANCELADA)
                .select_related('morador','area','area__condominio')
                .order_by('fim')[:20]
            ),
            "reservas_proximas": (
                Reserva.objects.filter(inicio__date__gte=hoje)
                .exclude(status=Reserva.Status.CANCELADA)
                .exclude(inicio__lte=agora, fim__gt=agora)
                .select_related('morador','area','area__condominio')
                .order_by("inicio")[:20]
            ),
            "agora": agora,
            "avisos": Aviso.objects.all()[:6],
        }
        return render(request, "portal/dashboard_gestor.html", ctx)

   
    if role == "PORTEIRO":
        ctx = {}
        reservas_hoje = (
            Reserva.objects.filter(inicio__date=hoje)
            .exclude(status=Reserva.Status.CANCELADA)
            .select_related("morador", "area", "area__condominio")
            .order_by("inicio")
        )
        ctx["reservas_hoje"] = reservas_hoje
        ctx["em_uso_agora"] = (
            Reserva.objects.filter(inicio__lte=agora, fim__gt=agora)
            .exclude(status=Reserva.Status.CANCELADA)
            .select_related("morador", "area", "area__condominio")
            .order_by("fim")
        )
        ctx["agora"] = agora
        return render(request, "portal/dashboard_porteiro.html", ctx)

    # MORADOR
    minhas = (
        Reserva.objects.filter(morador=request.user, fim__gt=agora)
        .exclude(status=Reserva.Status.CANCELADA)
        .select_related("area","area__condominio")
        .order_by("inicio")[:10]
    )
    cond = Unidade.objects.filter(morador=request.user).select_related("condominio").first()
    asm_qs = Assembleia.objects.filter(quando__gte=agora, condominio=cond.condominio) if cond else Assembleia.objects.none()

    ctx = {
        "minhas_reservas": minhas,
        "meus_lancamentos": (
            Lancamento.objects.filter(
                Q(unidade__morador=request.user)
                | Q(morador_alvo=request.user)
                | Q(destinatarios=request.user)
            ).order_by("-vencimento")[:10]
        ),
        "eventos": Evento.objects.all().order_by("id")[:6],  # ajuste se tiver campo de data
        "assembleias_proximas": asm_qs.order_by("quando")[:6],
        "agora": agora,
        "cancelaveis_ids": [r.id for r in minhas if r.inicio > agora],
        "avisos": Aviso.objects.all()[:6],
    }
    return render(request, "portal/dashboard_morador.html", ctx)