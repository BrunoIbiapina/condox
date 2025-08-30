# assembleias/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from uuid import uuid4

from condominios.models import Condominio


def ata_convocacao_path(instance, filename):
    # media/assembleias/<condominio_id>/<pauta_id_ou_tmp>/convocacao/<arquivo>
    base = instance.pk or f"tmp-{uuid4().hex[:8]}"
    cond = instance.condominio_id or "sem-cond"
    return f"assembleias/{cond}/{base}/convocacao/{filename}"


def ata_final_path(instance, filename):
    # media/assembleias/<condominio_id>/<pauta_id_ou_tmp>/ata/<arquivo>
    base = instance.pk or f"tmp-{uuid4().hex[:8]}"
    cond = instance.condominio_id or "sem-cond"
    return f"assembleias/{cond}/{base}/ata/{filename}"


class AssembleiaQuerySet(models.QuerySet):
    def visiveis_para(self, user):
        """
        Regra de visibilidade:
          - Se tiver destinatários definidos: o user precisa estar neles
          - Se NÃO tiver destinatários: visível para todos os moradores do condomínio
        Obs: se seu User tiver relação direta com condomínio, filtre aqui.
        """
        if not user.is_authenticated:
            return self.none()
        return self.filter(
            models.Q(destinatarios__isnull=True) | models.Q(destinatarios=user)
        ).distinct()

    def futuras(self):
        return self.filter(quando__gte=timezone.now()).order_by("quando")

    def passadas(self):
        return self.filter(quando__lt=timezone.now()).order_by("-quando")


class Assembleia(models.Model):
    titulo = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    quando = models.DateTimeField(help_text="Data e hora da assembleia")

    # Escopo
    condominio = models.ForeignKey(
        Condominio,
        on_delete=models.CASCADE,
        related_name="assembleias",
        help_text="Condomínio ao qual a assembleia pertence",
    )

    # (Opcional) restringir a destinatários específicos
    destinatarios = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="assembleias_destinadas",
        blank=True,
        help_text="Se vazio, todos os moradores do condomínio verão.",
    )

    # Anexos
    convocacao_pdf = models.FileField(
        upload_to=ata_convocacao_path,
        blank=True,
        null=True,
        help_text="Edital/Convocação (PDF)",
    )
    ata_pdf = models.FileField(
        upload_to=ata_final_path,
        blank=True,
        null=True,
        help_text="Ata final da reunião (PDF)",
    )

    # Auditoria
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assembleias_criadas",
    )

    objects = AssembleiaQuerySet.as_manager()

    class Meta:
        ordering = ["-quando", "-criado_em"]

    def __str__(self):
        return self.titulo

    @property
    def ja_ocorreu(self):
        return self.quando <= timezone.now()