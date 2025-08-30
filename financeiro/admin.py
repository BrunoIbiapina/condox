# financeiro/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Lancamento


@admin.register(Lancamento)
class LancamentoAdmin(admin.ModelAdmin):
    """
    Admin de Lançamentos com coluna 'Destino' indicando para quem a cobrança aparece
    no portal (morador da unidade, morador direto e/ou grupo de destinatários).
    """

    # ---- LISTA ----
    list_display = (
        'resumo',         # título compacto
        'destino',        # badge do destino
        'status',         # PAGO / PENDENTE / VENCIDO (property)
        'vencimento',
        'valor',
    )
    list_filter = (
        'tipo',
        ('vencimento', admin.DateFieldListFilter),
        ('pago_em', admin.DateFieldListFilter),
    )
    search_fields = (
        'descricao',
        'unidade__identificacao',
        'unidade__morador__username',
        'unidade__morador__first_name',
        'unidade__morador__last_name',
        'morador_alvo__username',
        'morador_alvo__first_name',
        'morador_alvo__last_name',
    )
    date_hierarchy = 'vencimento'
    ordering = ('-vencimento', '-criado_em')

    # ---- FORM ----
    autocomplete_fields = ('unidade', 'morador_alvo', 'destinatarios')
    filter_horizontal = ('destinatarios',)

    fieldsets = (
        ('Destinatários', {
            'fields': ('unidade', 'morador_alvo', 'destinatarios'),
            'description': (
                "Escolha para quem a cobrança aparece no portal do morador:<br>"
                "• <strong>Unidade</strong>: o morador atual da unidade verá o lançamento.<br>"
                "• <strong>Morador alvo</strong>: direciona para um usuário específico.<br>"
                "• <strong>Destinatários</strong>: um grupo de usuários (Muitos-para-Muitos)."
            )
        }),
        ('Dados do lançamento', {
            'fields': ('tipo', 'competencia', 'vencimento', 'valor', 'descricao')
        }),
        ('Pagamento', {
            'fields': ('pago_em',),
        }),
        ('Metadados', {
            'fields': ('criado_em',),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('criado_em',)

    # ---- EXIBIÇÕES AUXILIARES ----
    def resumo(self, obj):
        """Linha compacta para a listagem."""
        return f"{obj.get_tipo_display()} • R$ {obj.valor} • vence {obj.vencimento:%d/%m/%Y}"
    resumo.short_description = "Lançamento"

    def destino(self, obj):
        """
        Badge amigável de destino:
        - Unidade → <morador da unidade>
        - Direto  → <morador_alvo>
        - Grupo   → <n> moradores
        """
        partes = []

        # Unidade → morador atual (se houver)
        u = getattr(obj, 'unidade', None)
        if u:
            mor = getattr(u, 'morador', None)
            if mor:
                partes.append(
                    '<span class="badge badge-info">Unidade → {}</span>'.format(
                        mor.get_full_name() or mor.username
                    )
                )
            else:
                partes.append('<span class="badge badge-secondary">Unidade (sem morador)</span>')

        # Morador direto
        if obj.morador_alvo_id:
            nome = obj.morador_alvo.get_full_name() or obj.morador_alvo.username
            partes.append('<span class="badge badge-primary">Direto → {}</span>'.format(nome))

        # Grupo (M2M)
        if obj.pk and obj.destinatarios.exists():
            partes.append('<span class="badge badge-warning">Grupo → {} moradore(s)</span>'.format(
                obj.destinatarios.count()
            ))

        if not partes:
            partes.append('<span class="badge badge-light">—</span>')

        return format_html(" ".join(partes))

    destino.short_description = "Destino"