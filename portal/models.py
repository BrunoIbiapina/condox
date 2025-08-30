# financeiro/models.py
from django.db import models
from django.utils import timezone
from django.conf import settings
from condominios.models import Unidade

def boleto_upload_path(instance, filename):
    # media/financeiro/lancamentos/<id>/boleto/<arquivo>
    return f"financeiro/lancamentos/{instance.id or 'novo'}/boleto/{filename}"

def comprovante_upload_path(instance, filename):
    # media/financeiro/lancamentos/<id>/comprovantes/<arquivo>
    return f"financeiro/lancamentos/{instance.id or 'novo'}/comprovantes/{filename}"

class Lancamento(models.Model):
    class Tipo(models.TextChoices):
        COTA = 'COTA', 'Cota condominial'
        EXTRA = 'EXTRA', 'Extra/Rateio'
        DESPESA = 'DESPESA', 'Despesa'

    unidade = models.ForeignKey(
        Unidade, on_delete=models.SET_NULL, null=True, blank=True, related_name='lancamentos',
        help_text="Se marcado, o morador atual da unidade verá este lançamento."
    )
    # 👉 Destinatário direto (um morador específico)
    morador_alvo = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='lancamentos_diretos',
        help_text="Use para endereçar esta cobrança a um morador específico."
    )
    # 👉 Vários destinatários (opcional)
    destinatarios = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name='lancamentos_recebidos',
        help_text="Selecione se a cobrança for para vários moradores."
    )

    tipo = models.CharField(max_length=12, choices=Tipo.choices, default=Tipo.COTA)
    competencia = models.DateField(help_text="Mês/ano de referência")
    vencimento = models.DateField()
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    pago_em = models.DateField(null=True, blank=True)
    descricao = models.CharField(max_length=180, blank=True)

    # 🔽 NOVOS CAMPOS DE ARQUIVO
    boleto_pdf = models.FileField(
        upload_to=boleto_upload_path, null=True, blank=True,
        help_text="Anexe o boleto/2ª via ou documento de cobrança (opcional)."
    )
    comprovante_pdf = models.FileField(
        upload_to=comprovante_upload_path, null=True, blank=True,
        help_text="Comprovante enviado pelo morador."
    )
    comprovante_enviado_em = models.DateTimeField(null=True, blank=True)

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-vencimento', '-criado_em']

    # --- status calculado (mantém seu padrão) ---
    @property
    def status(self):
        if self.pago_em:
            return 'PAGO'
        if self.vencimento < timezone.localdate():
            return 'VENCIDO'
        return 'PENDENTE'

    @property
    def status_color(self):
        # usado no dashboard do morador
        return {
            'PAGO':     '#16a34a',  # verde
            'PENDENTE': '#f59e0b',  # âmbar
            'VENCIDO':  '#ef4444',  # vermelho
        }.get(self.status, '#64748b')

    # --- validação leve: precisa ter pelo menos UM destino ---
    def clean(self):
        has_unit = bool(self.unidade_id)
        has_direct = bool(self.morador_alvo_id)
        has_many = self.destinatarios.exists() if self.pk else False  # M2M só existe após salvar
        if not (has_unit or has_direct or has_many):
            from django.core.exceptions import ValidationError
            raise ValidationError("Defina pelo menos um destinatário: Unidade, Morador alvo ou Destinatários.")

    def marcar_comprovante(self):
        self.comprovante_enviado_em = timezone.now()

    def __str__(self):
        base = f"{self.get_tipo_display()} • {self.valor} • vence {self.vencimento:%d/%m/%Y}"
        return base