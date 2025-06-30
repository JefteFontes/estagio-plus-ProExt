from django.db import models
from django.core.validators import RegexValidator, MaxValueValidator, MinValueValidator
from django.forms import ValidationError
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator

from datetime import timedelta, date
import uuid


class TurnoChoices(models.TextChoices):
    MANHA = "Manhã"
    TARDE = "Tarde"
    NOITE = "Noite"

class Endereco(models.Model):
    rua = models.CharField(max_length=255)
    numero = models.CharField(max_length=10)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=50)
    cep = models.CharField(
        max_length=20,
        validators=[RegexValidator(regex="^[0-9]+$", message="Use apenas números.")],
    )
    complemento = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.rua}, {self.numero} - {self.bairro}"

class Instituicao(models.Model):
    cnpj = models.CharField(
        max_length=14,
        unique=True,
        validators=[RegexValidator(regex="^[0-9]{14}$", message="Use apenas números.")],
    )
    nome = models.CharField(max_length=250)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20)
    endereco = models.ForeignKey(
        Endereco, on_delete=models.PROTECT, null=True, blank=True
    )
    logo = models.ImageField(upload_to="instituicao_logos/", null=True, blank=True)

    def __str__(self):
        return self.nome

class Empresa(models.Model):
    instituicao = models.ForeignKey(Instituicao, on_delete=models.PROTECT)
    convenio = models.CharField(
        max_length=80,
        null=True,
        blank=True,
        unique=True,
        validators=[
            RegexValidator(regex=r"^[0-9]{4}/[0-9]{4}$", message="Use apenas números.")
        ],
    )
    empresa_nome = models.CharField(
        max_length=250,
        validators=[
            RegexValidator(regex=r"^[a-zA-Z ]+$", message="Use apenas letras.")
        ],
    )
    cnpj = models.CharField(
        max_length=250,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^[0-9]{2}\.[0-9]{3}\.[0-9]{3}/[0-9]{4}-[0-9]{2}$",
                message="Use apenas números.",
            )
        ],
    )
    razao_social = models.CharField(max_length=250)
    email = models.EmailField(unique=True)
    atividades = models.TextField(max_length=500, null=True)
    endereco = models.ForeignKey(
        Endereco, on_delete=models.PROTECT, null=True, blank=True
    )

    def __str__(self):
        return self.empresa_nome


class Areachoices(models.TextChoices):
    saude = "Saúde"
    tecnologia = "Tecnologia"
    gestao_e_negocios = "Gestão e Negócios"
    engenharia_e_construcao = "Engenharia e Construção"
    eletronica_e_automacao = "Eletrônica e Automação"
    educacao = "Educação"
    outros = "Outros"


class Cursos(models.Model):
    instituicao = models.ForeignKey(Instituicao, on_delete=models.PROTECT)
    nome_curso = models.CharField(
        max_length=50,
        null=False,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^[a-zA-ZáéíóúÁÉÍÓÚãõÃÕçÇ\s]+$", message="Use apenas letras."
            )
        ],
    )
    descricao = models.CharField(max_length=250)
    area = models.CharField(
        max_length=50, choices=Areachoices.choices, default=Areachoices.tecnologia
    )
    coordenador = models.CharField(max_length=50)
    email_coordenador = models.EmailField(max_length=254)

    def __str__(self):
        return f"{self.nome_curso}"



    
class Aluno(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    nome_completo = models.CharField(max_length=100)
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
    periodo = models.IntegerField(
        null=True,
        blank=True,
        default=4,
        validators=[
            RegexValidator(regex=r"^[0-9]+$", message="Use apenas números."),
            MaxValueValidator(12, message="O valor não pode ser maior que 12"),
            MinValueValidator(1, message="O valor não pode ser menor que 1"),
        ],
    )
    status = models.BooleanField(default=False)
    ira = models.FloatField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(0.0, message="O IRA não pode ser menor que 0.0"),
            MaxValueValidator(10.0, message="O IRA não pode ser maior que 10.0"),
        ],
        verbose_name="Índice de Rendimento Acadêmico",
    )

    instituicao = models.ForeignKey(
        Instituicao, on_delete=models.PROTECT, null=True, blank=True
    )
    curso = models.ForeignKey(Cursos, on_delete=models.PROTECT, null=True, blank=True)
    turno = models.TextField(choices=TurnoChoices.choices, default=TurnoChoices.MANHA)
    endereco = models.ForeignKey(
        Endereco, on_delete=models.PROTECT, null=True, blank=True
    )


    def __str__(self):
        return f"{self.nome_completo}"


class CoordenadorExtensao(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.PROTECT,
    )
    cpf = models.CharField(
        max_length=15,
        unique=True,
        validators=[RegexValidator(regex="^[0-9]+$", message="Use apenas números.")],
    )
    email = models.EmailField(unique=True)
    nome_completo = models.CharField(max_length=150)
    instituicao = models.ForeignKey(
        Instituicao, on_delete=models.PROTECT, null=True, blank=True
    )

    def __str__(self):
        return f"{self.nome_completo}"


class Supervisor(models.Model):
    cpf = models.CharField(
        max_length=14,
        unique=True,
        validators=[RegexValidator(regex="^[0-9]+$", message="Use apenas números.")],
    )
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20)
    nome_completo = models.CharField(max_length=150)
    cargo = models.CharField(max_length=254)
    empresa = models.ForeignKey(
        Empresa, on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        return f"{self.nome_completo}"



class StatusChoices(models.TextChoices):
    em_andamento = "Em andamento"
    concluido = "Concluído"


class TipoChoices(models.TextChoices):
    nao_obrigatorio = "Não obrigatório"
    obrigatorio = "Obrigatório"


class Estagio(models.Model):
    bolsa_estagio = models.FloatField(blank=True, null=True, default=0)
    area = models.CharField(max_length=250)
    tipo_estagio = models.TextField(
        choices=TipoChoices.choices, default=TipoChoices.nao_obrigatorio
    )
    status = models.TextField(
        choices=StatusChoices.choices, default=StatusChoices.em_andamento
    )
    descricao = models.TextField(max_length=1000)
    data_inicio = models.DateField()
    data_fim = models.DateField()
    turno = models.TextField(choices=TurnoChoices.choices, default=TurnoChoices.MANHA)
    auxilio_transporte = models.FloatField(blank=True, null=True, default=0)
    estagiario = models.ForeignKey(
        Aluno, on_delete=models.PROTECT, null=True, blank=False
    )
    empresa = models.ForeignKey(
        Empresa, on_delete=models.PROTECT, null=True, blank=True
    )
    supervisor = models.ForeignKey(
        Supervisor, on_delete=models.PROTECT, null=True, blank=True
    )
    instituicao = models.ForeignKey(
        Instituicao, on_delete=models.PROTECT, null=True, blank=True
    )
    orientador = models.TextField(max_length=100, null=True, blank=True)
    pdf_termo = models.FileField(upload_to='temp_docs/', null=True, blank=True)
def clean(self):
    super().clean()
    
    if not self.estagiario:
        raise ValidationError({'estagiario': 'Selecione um estagiário'})
    
    if self.data_inicio and self.data_fim:
        if self.data_fim < self.data_inicio:
            raise ValidationError({
                'data_fim': 'A data de término não pode ser anterior à data de início (validação do modelo).'
            })
    
    if hasattr(self.estagiario, 'periodo') and self.estagiario.periodo < 4:
        raise ValidationError({
            'estagiario': 'O estudante precisa estar cursando e concluído no mínimo 03 (três) período letivos do curso'
        })
    
    if hasattr(self.estagiario, 'turno') and self.estagiario.turno == self.turno:
        raise ValidationError({
            'turno': 'O turno do estagiário e o turno do estágio devem ser diferentes.'
        })

    if self.supervisor and self.empresa and self.supervisor.empresa != self.empresa:
        raise ValidationError({
            'empresa': 'O supervisor precisa estar vinculado à mesma empresa do estagiário.'
        })
    
    if hasattr(self.estagiario, 'ira') and (self.estagiario.ira is None or self.estagiario.ira < 6.0):
        raise ValidationError({
            'estagiario': 'O estudante precisa ter Índice de Rendimento Acadêmico (IRA) igual ou superior a 6.0'
        })

            
       

    def __str__(self):
       return f"Estágio: {self.estagiario.nome_completo} em {self.empresa.empresa_nome} ({self.get_status_display()})"



TIPOS_RELATORIO = [
    ("termo", "Termo de Compromisso"),
    ("relatorio_semestral", "Relatório Semestral de Atividades"),
    ("avaliacao", "Relatório de Avaliação"),
    ("conclusao", "Termo de Conclusão/Rescisão"),
]


class RelatorioEstagio(models.Model):
    estagio = models.ForeignKey("Estagio", on_delete=models.CASCADE)
    tipo = models.CharField(max_length=30, choices=TIPOS_RELATORIO)
    data_prevista = models.DateField()
    arquivo = models.FileField(upload_to="relatorios/", null=True, blank=True)
    preenchido = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.estagio.estagiario}"


class EstagiarioInvite(models.Model):
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    instituicao = models.ForeignKey('Instituicao', on_delete=models.CASCADE)
    coordenador = models.ForeignKey('CoordenadorExtensao', on_delete=models.CASCADE)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)
