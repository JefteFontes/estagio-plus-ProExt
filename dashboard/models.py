from django.db import models
from django.core.validators import RegexValidator
from django.forms import ValidationError
from django.contrib.auth.models import User
from datetime import timedelta, date


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
    telefone = models.CharField(
        max_length=20,
    )
    endereco = models.ForeignKey(
        Endereco, on_delete=models.PROTECT, null=True, blank=True
    )

    def __str__(self):
        return self.nome


class CoordenadorExtensao(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, )
    cpf = models.CharField(max_length=15, unique=True, validators=[RegexValidator(regex='^[0-9]+$', message='Use apenas números.')])
    email = models.EmailField(unique=True)
    primeiro_nome = models.CharField(max_length=50)
    sobrenome = models.CharField(max_length=50)
    instituicao = models.ForeignKey(Instituicao, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.primeiro_nome} {self.sobrenome}"


class Empresa(models.Model):
    instituicao = models.ForeignKey(Instituicao, on_delete=models.PROTECT)
    empresa_nome = models.CharField(max_length=250)
    cnpj = models.CharField(max_length=250)
    razao_social = models.CharField(max_length=250)
    email = models.EmailField(unique=True)
    atividades = models.TextField(max_length=500, null=True)
    endereco = models.ForeignKey(Endereco, on_delete=models.PROTECT, null=True, blank=True)
    
    def __str__(self):
        return self.empresa_nome


class Areachoices(models.TextChoices):
    saude = "Saude"
    tecnologia = "Tecnologia"
    gestao_e_negocios = "Gestão e Negocios"
    engenharia_e_construcao = "Engenharia e Construção"
    eletronica_e_automacao = "Eletronica e Automacao"
    educacao = "Educacao"
    outros = "Outros"


class Cursos(models.Model):
    instituicao = models.ForeignKey(Instituicao, on_delete=models.PROTECT)
    nome_curso = models.CharField(max_length=50)
    descricao = models.CharField(max_length=250)
    area = models.CharField(
        max_length=50, choices=Areachoices.choices, default=Areachoices.tecnologia
    )
    coordenador = models.CharField(max_length=50)
    email_coordenador = models.EmailField(max_length=254)

    def __str__(self):
        return f"{self.nome_curso}"


class Estagiario(models.Model):
    primeiro_nome = models.CharField(max_length=50)
    sobrenome = models.CharField(max_length=50)
    cpf = models.CharField(
        max_length=14,
        unique=True,
        validators=[
            RegexValidator(regex="^[0-9]+$", message="Use apenas números.")
        ],
    )
    matricula = models.CharField(max_length=55)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20)
    curso = models.ForeignKey(Cursos, on_delete=models.PROTECT, null=True, blank=True)
    status = models.BooleanField(default=False)
    endereco = models.ForeignKey(Endereco, on_delete=models.PROTECT, null=True, blank=True)
    instituicao = models.ForeignKey(Instituicao, on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        return f"{self.primeiro_nome} {self.sobrenome}"


class CoordenadorExtensao(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT, )
    cpf = models.CharField(max_length=15, unique=True, validators=[RegexValidator(regex='^[0-9]+$', message='Use apenas números.')])
    email = models.EmailField(unique=True)
    primeiro_nome = models.CharField(max_length=50)
    sobrenome = models.CharField(max_length=50)
    instituicao = models.ForeignKey(Instituicao, on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        return f"{self.primeiro_nome} {self.sobrenome}"


class Supervisor(models.Model):
    cpf = models.CharField(
        max_length=14,
        unique=True,
        validators=[RegexValidator(regex="^[0-9]+$", message="Use apenas números.")],
    )
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20)
    primeiro_nome = models.CharField(max_length=50)
    sobrenome = models.CharField(max_length=50)
    cargo = models.CharField(max_length=254)
    empresa = models.ForeignKey(
        Empresa, on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        return f"{self.primeiro_nome} {self.sobrenome}"


class TurnoChoices(models.TextChoices):
    MANHA = "Manha"
    TARDE = "Tarde"
    NOITE = "Noite"


class StatusChoices(models.TextChoices):
    em_andamento = "Em andamento"
    concluido = "Concluido"

class TipoChoices(models.TextChoices):
    nao_obrigatorio = 'Não obrigatório'
    obrigatorio = 'Obrigatório'

class TipoChoices(models.TextChoices):
    obrigatorio = 'Obrigatório'
    nao_obrigatorio = 'Não obrigatório'


class Estagio(models.Model):
    bolsa_estagio = models.FloatField(blank=True, null=True, default=0)
    area = models.CharField(max_length=250)
    tipo_estagio = models.TextField(choices = TipoChoices.choices, default=TipoChoices.nao_obrigatorio)
    status = models.TextField(choices=StatusChoices.choices, default=StatusChoices.em_andamento)
    descricao = models.TextField(max_length=1000)
    data_inicio = models.DateField()
    data_fim = models.DateField()
    turno = models.TextField(choices=TurnoChoices.choices, default=TurnoChoices.MANHA)
    auxilio_transporte = models.FloatField(blank=True, null=True,default=0)
    estagiario = models.ForeignKey(Estagiario, on_delete=models.PROTECT, null=True, blank=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT, null=True, blank=True)
    supervisor = models.ForeignKey(Supervisor, on_delete=models.PROTECT, null=True, blank=True)
    instituicao = models.ForeignKey(Instituicao, on_delete=models.PROTECT, null=True, blank=True)
    orientador = models.TextField(max_length=100, null=True, blank=True)
    def clean(self):
        return f"{self.area} - {self.status}"
    def __str__(self):
        return f"{self.area} - {self.status}"


class ImportTermoEstagio(models.Model):
    file = models.FileField(upload_to="termo_estagio/%Y/%m/%d/")

    def __str__(self):
        return f"{self.file}"
