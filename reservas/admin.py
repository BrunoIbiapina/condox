from django.contrib import admin
from django.utils.html import format_html
from .models import AreaReservavel, Reserva


# ---------- AreaReservavel ----------
@admin.register(AreaReservavel)
class AreaReservavelAdmin(admin.ModelAdmin):
    list_display = ("nome", "condominio", "janela", "dias_permitidos_str", "bloqueios_qtd")
    list_filter = ("condominio",)
    search_fields = ("nome", "condominio__nome")
    ordering = ("condominio__nome", "nome")

    @admin.display(description="Janela")
    def janela(self, obj: AreaReservavel):
        h1 = obj.hora_inicio.strftime("%H:%M") if obj.hora_inicio else "00:00"
        h2 = obj.hora_fim.strftime("%H:%M") if obj.hora_fim else "23:59"
        return f"{h1}–{h2}"

    @admin.display(description="Dias")
    def dias_permitidos_str(self, obj: AreaReservavel):
        if obj.dias_permitidos:
            return ", ".join(str(d) for d in obj.dias_permitidos) + " (0=Seg..6=Dom)"
        return "Todos"

    @admin.display(description="Datas bloqueadas")
    def bloqueios_qtd(self, obj: AreaReservavel):
        return len(obj.datas_bloqueadas or [])


# ---------- Reserva ----------
STATUS_COLORS = {
    "APROVADA": "#16a34a",   # verde
    "PENDENTE": "#f59e0b",   # âmbar
    "CANCELADA": "#64748b",  # cinza
}

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ("area", "morador", "periodo", "status_badge")
    list_filter = ("status", "area__condominio", "area")
    search_fields = ("morador__username", "morador__first_name", "morador__last_name", "area__nome")
    date_hierarchy = "inicio"
    ordering = ("-inicio",)
    autocomplete_fields = ("area", "morador")
    actions = ("aprovar_reservas", "cancelar_reservas")

    @admin.display(description="Período")
    def periodo(self, obj: Reserva):
        return f"{obj.inicio:%d/%m/%Y %H:%M} – {obj.fim:%H:%M}"

    @admin.display(description="Status")
    def status_badge(self, obj: Reserva):
        cor = STATUS_COLORS.get(obj.status, "#94a3b8")
        return format_html(
            '<span style="background:{};color:#fff;border-radius:999px;padding:2px 8px;font-size:12px;">{}</span>',
            cor, obj.get_status_display()
        )

    @admin.action(description="Marcar como APROVADA")
    def aprovar_reservas(self, request, queryset):
        updated = queryset.update(status=Reserva.Status.APROVADA)
        self.message_user(request, f"{updated} reserva(s) marcada(s) como APROVADA.")

    @admin.action(description="Marcar como CANCELADA")
    def cancelar_reservas(self, request, queryset):
        updated = queryset.update(status=Reserva.Status.CANCELADA)
        self.message_user(request, f"{updated} reserva(s) marcada(s) como CANCELADA.")