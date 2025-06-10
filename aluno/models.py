from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator

from dashboard.models import Cursos, Endereco, Instituicao, TurnoChoices


class Aluno(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    nome = models.CharField(max_length=100)
    cpf = models.CharField(
        max_length=14,
        unique=True,
        validators=[RegexValidator(regex=r"^[0-9]+$", message="Use apenas números.")],
    )
    matricula = models.CharField(
        max_length=55,
        null=True,
        blank=True,
        unique=True,
    )
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20)
    curso = models.ForeignKey(Cursos, on_delete=models.PROTECT, null=True, blank=True)
    periodo = models.IntegerField(
        null=True,
        blank=True,
        default=4,
        validators=[
            RegexValidator(regex=r"^[0-9]+$", message="Use apenas números."),
            MaxValueValidator(8, message="O valor não pode ser maior que 8"),
            MinValueValidator(1, message="O valor não pode ser menor que 1"),
        ],
    )
    turno = models.TextField(choices=TurnoChoices.choices, default=TurnoChoices.MANHA)
    status = models.BooleanField(default=False)
    endereco = models.ForeignKey(
        Endereco, on_delete=models.PROTECT, null=True, blank=True
    )
    instituicao = models.ForeignKey(
        Instituicao, on_delete=models.PROTECT, null=True, blank=True
    )

    ira = models.FloatField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(0.0, message="O IRA não pode ser menor que 0.0"),
            MaxValueValidator(10.0, message="O IRA não pode ser maior que 10.0"),
        ],
        verbose_name="Índice de Rendimento Acadêmico",
    )

    def __str__(self):
        return f"{self.nome}"
