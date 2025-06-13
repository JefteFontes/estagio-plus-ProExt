from django.db import models
from base.models import InstituicaoLegal
from dashboard.models import Endereco


class Instituicao(InstituicaoLegal):
    endereco = models.ForeignKey(
        Endereco, on_delete=models.PROTECT, null=True, blank=True
    )
    logo = models.ImageField(upload_to="instituicao_logos/", null=True, blank=True)

    def __str__(self):
        return self.nome
