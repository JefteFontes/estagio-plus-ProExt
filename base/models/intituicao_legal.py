from django.db import models
from django.core.validators import RegexValidator


class InstituicaoLegal(models.Model):
    cnpj = models.CharField(
        max_length=14,
        unique=True,
        validators=[RegexValidator(regex="^[0-9]{14}$", message="Use apenas números.")],
    )
    nome = models.CharField(max_length=250)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20)

    class Meta:
        abstract = True
