from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from condominios.models import Condominio
from django.conf import settings


class AreaReservavel(models.Model):
    condominio = models.ForeignKey(Condominio, on_delete=models.CASCADE, related_name='areas')
    nome = models.CharField(max_length=120)
    descricao = models.TextField(blank=True)
    # 0=Seg ... 6=Dom
    dias_permitidos = models.JSONField(default=list, blank=True)
    hora_inicio = models.TimeField(null=True, blank=True)
    hora_fim = models.TimeField(null=True, blank=True)
    # ['2025-12-25']
    datas_bloqueadas = models.JSONField(default=list, blank=True)

    def __str__(self):
        return f"{self.condominio} - {self.nome}"


class Reserva(models.Model):
    class Status(models.TextChoices):
        PENDENTE = 'PENDENTE', 'Pendente'
        APROVADA = 'APROVADA', 'Aprovada'
        CANCELADA = 'CANCELADA', 'Cancelada'

    area = models.ForeignKey(AreaReservavel, on_delete=models.CASCADE, related_name='reservas')
    morador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reservas')
    inicio = models.DateTimeField()
    fim = models.DateTimeField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDENTE)
    observacoes = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    # NOVO: se True, esta reserva permite compartilhamento do espaço com outros moradores
    permite_compartilhar = models.BooleanField(default=False)

    class Meta:
        ordering = ['inicio']

    def clean(self):
        # início/fim válidos
        if self.inicio >= self.fim:
            raise ValidationError('Período inválido: início deve ser antes do fim.')

        # regras da área (dia permitido, janela de horário, datas bloqueadas)
        local_date = timezone.localtime(self.inicio).date()
        weekday = local_date.weekday()  # 0=Seg ... 6=Dom

        if self.area.dias_permitidos and weekday not in self.area.dias_permitidos:
            raise ValidationError('Dia da semana não permitido para esta área.')

        if self.area.hora_inicio and self.inicio.time() < self.area.hora_inicio:
            raise ValidationError('Horário de início antes do permitido.')
        if self.area.hora_fim and self.fim.time() > self.area.hora_fim:
            raise ValidationError('Horário de fim após o permitido.')

        if local_date.isoformat() in (self.area.datas_bloqueadas or []):
            raise ValidationError('Esta data está bloqueada para reservas nesta área.')

        # conflitos com outras reservas (ignorando canceladas e a própria)
        qs = Reserva.objects.filter(area=self.area).exclude(pk=self.pk)
        qs = qs.exclude(status=Reserva.Status.CANCELADA)
        conflitos = list(qs.filter(inicio__lt=self.fim, fim__gt=self.inicio))

        if conflitos:
            # Se QUALQUER reserva conflitante NÃO permite compartilhar -> bloqueia
            # Só é permitido se TODAS as conflitantes tiverem permite_compartilhar=True
            if not all(r.permite_compartilhar for r in conflitos):
                raise ValidationError('Já existe reserva que conflita com este período.')

        # caso contrário, permitido (compartilhamento)

    def __str__(self):
        return f"{self.area.nome} ({self.inicio:%d/%m %H:%M}-{self.fim:%H:%M}) - {self.morador}"