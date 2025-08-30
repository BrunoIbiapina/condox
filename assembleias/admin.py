# assembleias/admin.py
from django.contrib import admin
from .models import Assembleia


@admin.register(Assembleia)
class AssembleiaAdmin(admin.ModelAdmin):
    list_display = ("titulo", "condominio", "quando", "tem_convocacao", "tem_ata", "criado_em")
    list_filter = ("condominio", ("quando", admin.DateFieldListFilter))
    search_fields = ("titulo", "descricao")
    autocomplete_fields = ("condominio", "destinatarios")
    readonly_fields = ("criado_em", "atualizado_em", "criado_por")

    fieldsets = (
        ("Informações", {
            "fields": ("titulo", "descricao", "quando", "condominio", "destinatarios")
        }),
        ("Anexos", {
            "fields": ("convocacao_pdf", "ata_pdf")
        }),
        ("Auditoria", {
            "fields": ("criado_em", "atualizado_em", "criado_por")
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.criado_por_id:
            obj.criado_por = request.user
        super().save_model(request, obj, form, change)

    @admin.display(boolean=True, description="Convocação")
    def tem_convocacao(self, obj):
        return bool(obj.convocacao_pdf)

    @admin.display(boolean=True, description="Ata final")
    def tem_ata(self, obj):
        return bool(obj.ata_pdf)