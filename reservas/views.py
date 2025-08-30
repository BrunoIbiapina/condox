# reservas/views.py
from datetime import datetime, timedelta, time
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ValidationError

from .models import AreaReservavel, Reserva
from .forms import ReservaForm  # mantido

SLOT_MINUTES = 60  # duração do slot

def _parse_date(query_param, default_date):
    try:
        return datetime.strptime(query_param, "%Y-%m-%d").date()
    except Exception:
        return default_date

def _slots_disponiveis(area: AreaReservavel, dia):
    """
    Gera slots livres (inicio, fim) para a data `dia`, respeitando:
    - dias_permitidos
    - hora_inicio / hora_fim
    - datas_bloqueadas
    - conflitos com reservas existentes (pendente ou aprovada)
    - oculta slots totalmente no passado quando a data é hoje
    """
    # regras do dia
    if area.dias_permitidos and dia.weekday() not in area.dias_permitidos:
        return []

    if area.datas_bloqueadas and dia.isoformat() in (area.datas_bloqueadas or []):
        return []

    # janelas
    h_ini = area.hora_inicio or time(0, 0)
    h_fim = area.hora_fim or time(23, 59)

    # timezone-aware
    tz = timezone.get_current_timezone()
    dt_ini = timezone.make_aware(datetime.combine(dia, h_ini), tz)
    dt_fim = timezone.make_aware(datetime.combine(dia, h_fim), tz)

    # reservas existentes no dia (exceto canceladas)
    existentes = Reserva.objects.filter(
        area=area, inicio__lt=dt_fim, fim__gt=dt_ini
    ).exclude(status=Reserva.Status.CANCELADA).order_by('inicio')

    slots = []
    cursor = dt_ini
    now = timezone.localtime()
    while cursor + timedelta(minutes=SLOT_MINUTES) <= dt_fim:
        slot_inicio = cursor
        slot_fim = cursor + timedelta(minutes=SLOT_MINUTES)

        # pular slots do passado (se é hoje)
        if dia == now.date() and slot_fim <= now:
            cursor = slot_fim
            continue

        conflito = existentes.filter(inicio__lt=slot_fim, fim__gt=slot_inicio).exists()
        if not conflito:
            slots.append((slot_inicio, slot_fim))
        cursor = slot_fim

    return slots

@login_required
def areas_list(request):
    areas = AreaReservavel.objects.all().order_by('condominio__nome', 'nome')
    return render(request, 'reservas/areas_list.html', {'areas': areas})

@login_required
def area_detail(request, area_id):
    area = get_object_or_404(AreaReservavel, pk=area_id)
    hoje = timezone.localdate()
    dia = _parse_date(request.GET.get('data') or hoje.isoformat(), hoje)
    slots = _slots_disponiveis(area, dia)

    role = getattr(request.user, 'role', 'MORADOR')
    pode_reservar = role != 'PORTEIRO'  # porteiro: apenas visualiza

    return render(request, 'reservas/area_detail.html', {
        'area': area,
        'dia': dia,
        'slots': slots,
        'is_hoje': dia == hoje,
        'now_str': timezone.localtime().strftime('%Y-%m-%d %H:%M'),
        'pode_reservar': pode_reservar,
    })

@login_required
def agendar(request):
    # 🔒 Porteiro não pode reservar
    role = getattr(request.user, 'role', 'MORADOR')
    if role == 'PORTEIRO':
        messages.error(request, 'Porteiro não pode criar reservas.')
        return HttpResponseForbidden('Porteiro não pode criar reservas.')

    if request.method != 'POST':
        return HttpResponseBadRequest('Método inválido.')

    area_id = request.POST.get('area_id')
    inicio = request.POST.get('inicio')  # ISO datetime
    fim = request.POST.get('fim')        # ISO datetime
    area = get_object_or_404(AreaReservavel, pk=area_id)

    try:
        dt_inicio = datetime.fromisoformat(inicio)
        dt_fim = datetime.fromisoformat(fim)
        tz = timezone.get_current_timezone()
        if timezone.is_naive(dt_inicio):
            dt_inicio = timezone.make_aware(dt_inicio, tz)
        if timezone.is_naive(dt_fim):
            dt_fim = timezone.make_aware(dt_fim, tz)
    except Exception:
        messages.error(request, 'Datas inválidas.')
        return redirect('reservas:area_detail', area_id=area.id)

    # cria reserva (já aprovando, conforme combinado)
    r = Reserva(
        area=area, morador=request.user,
        inicio=dt_inicio, fim=dt_fim,
        status=Reserva.Status.APROVADA
    )
    try:
        r.clean()
        r.save()
    except ValidationError as e:
        for msg in e.messages:
            messages.error(request, msg)
        return redirect(f"/reservas/areas/{area.id}/?data={dt_inicio.date().isoformat()}")

    messages.success(request, 'Reserva confirmada!')
    return redirect('portal:home')

@login_required
def cancelar_reserva(request, reserva_id):
    if request.method != 'POST':
        return HttpResponseBadRequest('Método inválido.')
    reserva = get_object_or_404(Reserva, pk=reserva_id)

    user_role = getattr(request.user, 'role', 'MORADOR')
    is_owner = reserva.morador_id == request.user.id
    is_gestor = user_role == 'GESTOR'
    if not (is_owner or is_gestor):
        return HttpResponseForbidden('Você não tem permissão para cancelar esta reserva.')

    now = timezone.localtime()
    if reserva.inicio <= now:
        messages.error(request, 'Não é possível cancelar uma reserva que já começou.')
        return redirect('portal:home')

    reserva.status = Reserva.Status.CANCELADA
    reserva.save(update_fields=['status'])

    messages.success(request, 'Reserva cancelada. O horário voltou a ficar disponível.')
    return redirect(request.META.get('HTTP_REFERER') or 'portal:home')

@login_required
def historico(request):
    hoje = timezone.localdate()
    default_de = hoje - timedelta(days=30)
    de_param = request.GET.get("de") or default_de.isoformat()
    ate_param = request.GET.get("ate") or hoje.isoformat()

    try:
        de = datetime.strptime(de_param, "%Y-%m-%d").date()
    except Exception:
        de = default_de
        de_param = default_de.isoformat()
    try:
        ate = datetime.strptime(ate_param, "%Y-%m-%d").date()
    except Exception:
        ate = hoje
        ate_param = hoje.isoformat()

    qs = Reserva.objects.filter(morador=request.user).order_by("-inicio")
    qs = qs.filter(inicio__date__gte=de, fim__date__lte=ate)
    reservas = qs[:100]

    return render(request, "reservas/historico.html", {
        "reservas": reservas,
        "de": de_param,
        "ate": ate_param,
    })