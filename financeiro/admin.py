# financeiro/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils.timezone import localtime
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
        'has_boleto',
        'has_comprovante',
        'comprovante_link_list',  # 👈 link clicável na listagem
    )
    list_filter = (
        'tipo',
        ('vencimento', admin.DateFieldListFilter),
        ('pago_em', admin.DateFieldListFilter),
        ('boleto_pdf', admin.EmptyFieldListFilter),
        ('comprovante_pdf', admin.EmptyFieldListFilter),
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
        ('Arquivos', {
            # 👇 mostramos os campos de arquivo e também um link readonly
            'fields': ('boleto_pdf', 'comprovante_pdf', 'comprovante_enviado_em', 'comprovante_link_detail'),
        }),
        ('Pagamento', {
            'fields': ('pago_em',),
        }),
        ('Metadados', {
            'fields': ('criado_em',),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('criado_em', 'comprovante_enviado_em', 'comprovante_link_detail')

    # ---- EXIBIÇÕES AUXILIARES ----
    def resumo(self, obj):
        return f"{obj.get_tipo_display()} • R$ {obj.valor} • vence {obj.vencimento:%d/%m/%Y}"
    resumo.short_description = "Lançamento"

    def destino(self, obj):
        partes = []
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
        if obj.morador_alvo_id:
            nome = obj.morador_alvo.get_full_name() or obj.morador_alvo.username
            partes.append('<span class="badge badge-primary">Direto → {}</span>'.format(nome))
        if obj.pk and obj.destinatarios.exists():
            partes.append('<span class="badge badge-warning">Grupo → {} moradore(s)</span>'.format(
                obj.destinatarios.count()
            ))
        if not partes:
            partes.append('<span class="badge badge-light">—</span>')
        return format_html(" ".join(partes))
    destino.short_description = "Destino"

    def has_boleto(self, obj):
        return bool(obj.boleto_pdf)
    has_boleto.short_description = "Boleto?"
    has_boleto.boolean = True

    def has_comprovante(self, obj):
        return bool(obj.comprovante_pdf)
    has_comprovante.short_description = "Comprovante?"
    has_comprovante.boolean = True

    # ---- LINKS PARA O COMPROVANTE ----
    def comprovante_link_list(self, obj):
        """
        Na LISTA: mostra link 'Abrir' + quando foi enviado (pequeno).
        """
        if not obj.comprovante_pdf:
            return "—"
        quando = obj.comprovante_enviado_em
        quando_fmt = localtime(quando).strftime("%d/%m %H:%M") if quando else "—"
        return format_html(
            '<a href="{}" target="_blank">📎 Abrir</a><br><small class="text-muted">{}</small>',
            obj.comprovante_pdf.url,
            f"enviado {quando_fmt}"
        )
    comprovante_link_list.short_description = "Comprovante"

    def comprovante_link_detail(self, obj):
        """
        Na PÁGINA DE EDIÇÃO do admin (readonly): link grande, se existir.
        """
        if not obj.comprovante_pdf:
            return "—"
        return format_html('<a href="{}" target="_blank">📎 Abrir comprovante</a>', obj.comprovante_pdf.url)
    comprovante_link_detail.short_description = "Abrir comprovante"