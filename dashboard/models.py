from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
import re


class Endereco(models.Model):
    rua = models.CharField(max_length=255, validators=[ RegexValidator(regex='^[A-Za-z\s]+$',message='Use apenas letras e espaços.')])
    numero = models.CharField(max_length=10, validators=[ RegexValidator(regex='^[0-9]+$',message='Use apenas números.')])
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=50)
    cep = models.CharField(max_length=20,validators=[ RegexValidator(regex='^[0-9]+$',message='Use apenas números.')])

    def __str__(self):
        return f'{self.rua}, {self.numero} - {self.bairro}'


class Empresa(models.Model):
    nome = models.CharField(max_length=250,validators=[ RegexValidator(regex='^[A-Za-z\s]+$',message='Use apenas letras e espaços.')])
    cnpj = models.CharField(max_length=250 ,validators=[ RegexValidator(regex='^[0-9]+$',message='Use apenas números.')])
    razao_social = models.CharField(max_length=250,validators=[ RegexValidator(regex='^[A-Za-z\s]+$',message='Use apenas letras e espaços.')])
    email = models.EmailField(unique=True,validators=[ RegexValidator(regex='^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',message='Email invalido.')])
    endereco = models.ForeignKey(Endereco, on_delete=models.CASCADE, null=True, blank=True,validators=[ RegexValidator(regex='^[A-Za-z\s]+$',message='Use apenas letras e espaços.')])

    def __str__(self):
        return self.nome


class Instituicao(models.Model):
    cnpj = models.CharField(max_length=20,validators=[ RegexValidator(regex='^[0-9]+$',message='Use apenas números.')])
    nome = models.CharField(max_length=250,validators=[ RegexValidator(regex='^[A-Za-z\s]+$',message='Use apenas letras e espaços.')])
    email = models.EmailField(unique=True, validators=[ RegexValidator(regex='^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',message='Email invalido.')])
    telefone = models.CharField(max_length=20,validators=[ RegexValidator(regex='^[0-9]+$',message='Use apenas números.')])
    endereco = models.ForeignKey(Endereco, on_delete=models.CASCADE, null=True, blank=True,validators=[ RegexValidator(regex='^[A-Za-z\s]+$',message='Use apenas letras e espaços.')])

    def __str__(self):
        return self.nome


class Estagiario(models.Model):
    primeiro_nome = models.CharField(max_length=50, validators=[ RegexValidator(regex='^[A-Za-z\s]+$',message='Use apenas letras e espaços.')])
    sobrenome = models.CharField(max_length=50, validators=[ RegexValidator(regex='^[A-Za-z\s]+$',message='Use apenas letras e espaços.')])
    cpf = models.CharField(max_length=12, unique=True,validators=[ RegexValidator(regex='^[0-9]+$',message='Use apenas números.')])
    matricula = models.CharField(max_length=55, validators=[ RegexValidator(regex='^[0-9]+$',message='Use apenas números.')])
    email = models.EmailField(unique=True,validators=[ RegexValidator(regex='^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',message='Email invalido.')])
    telefone = models.CharField(max_length=20,validators=[ RegexValidator(regex='^[0-9]+$',message='Use apenas números.')])
    curso = models.CharField(max_length=55, validators=[ RegexValidator(regex='^[A-Za-z\s]+$',message='Use apenas letras e espaços.')])
    status = models.BooleanField(default=False)
    endereco = models.ForeignKey(Endereco, on_delete=models.CASCADE, null=True, blank=True,validators=[ RegexValidator(regex='^[A-Za-z\s]+$',message='Use apenas letras e espaços.')])
    instituicao = models.ForeignKey(Instituicao, on_delete=models.CASCADE , null=True, blank=True,validators=[ RegexValidator(regex='^[A-Za-z\s]+$',message='Use apenas letras e espaços.')])

    def __str__(self):
        return f'{self.primeiro_nome} {self.sobrenome}'


class CoordenadorExtensao(models.Model):
    cpf = models.CharField(max_length=12, unique=True,validators=[ RegexValidator(regex='^[0-9]+$',message='Use apenas números.')])
    email = models.EmailField(unique=True,validators=[ RegexValidator(regex='^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',message='Email invalido.')])
    primeiro_nome = models.CharField(max_length=50,validators=[ RegexValidator(regex='^[A-Za-z\s]+$',message='Use apenas letras e espaços.')])
    sobrenome = models.CharField(max_length=50,validators=[ RegexValidator(regex='^[A-Za-z\s]+$',message='Use apenas letras e espaços.')])
    instituicao = models.ForeignKey(Instituicao, on_delete=models.CASCADE, null=True, blank=True,validators=[ RegexValidator(regex='^[A-Za-z\s]+$',message='Use apenas letras e espaços.')])

    def __str__(self):
        return f'{self.primeiro_nome} {self.sobrenome}'


class Supervisor(models.Model):
    cpf = models.CharField(max_length=50, unique=True,validators=[ RegexValidator(regex='^[0-9]+$',message='Use apenas números.')])
    email = models.EmailField(unique=True,validators=[ RegexValidator(regex='^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',message='Email invalido.')])
    telefone = models.CharField(max_length=20,validators=[ RegexValidator(regex='^[0-9]+$',message='Use apenas números.')])
    primeiro_nome = models.CharField(max_length=50,validators=[ RegexValidator(regex='^[A-Za-z\s]+$',message='Use apenas letras e espaços.')])
    sobrenome = models.CharField(max_length=50,validators=[ RegexValidator(regex='^[A-Za-z\s]+$',message='Use apenas letras e espaços.')])
    cargo = models.CharField(max_length=254,validators=[ RegexValidator(regex='^[A-Za-z\s]+$',message='Use apenas letras e espaços.')])
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, null=True, blank=True,validators=[ RegexValidator(regex='^[A-Za-z\s]+$',message='Use apenas letras e espaços.')])

    def __str__(self):
        return f'{self.primeiro_nome} {self.sobrenome}'


class TurnoChoices(models.TextChoices):
    MANHA = 'Manha'
    TARDE = 'Tarde'
    NOITE = 'Noite'


class StatusChoices(models.TextChoices):
    em_andamento = 'Em andamento'
    concluido = 'Concluido'


class Estagio(models.Model):
    bolsa_estagio = models.FloatField(blank=True, null=True, validators=[RegexValidator(regex='^[0-9]+$',message='Use apenas números.')])
    area = models.CharField(max_length=250,validators=[ RegexValidator(regex='^[A-Za-z\s]+$',message='Use apenas letras e espaços.')])
    status = models.TextField(choices=StatusChoices.choices, default=StatusChoices.em_andamento)
    descricao = models.TextField(max_length=1000,validators=[ RegexValidator(regex='^[A-Za-z\s]+$',message='Use apenas letras e espaços.')])
    data_inicio = models.DateField(max_length=10,validators=[ RegexValidator(regex='^[0-9]+$',message='Use apenas números.')])
    data_fim = models.DateField(max_length=10,validators=[ RegexValidator(regex='^[0-9]+$',message='Use apenas números.')])
    turno = models.TextField(choices=TurnoChoices.choices, default=TurnoChoices.MANHA)
    auxilio_transporte = models.FloatField(blank=True, null=True,default=0, validators=[RegexValidator(regex='^[0-9]+$',message='Use apenas números.')])
    estagiario = models.ForeignKey(Estagiario, on_delete=models.CASCADE, null=True, blank=True,validators=[ RegexValidator(regex='^[A-Za-z\s]+$',message='Use apenas letras e espaços.')])
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, null=True, blank=True,validators=[ RegexValidator(regex='^[A-Za-z\s]+$',message='Use apenas letras e espaços.')])
    supervisor = models.ForeignKey(Supervisor, on_delete=models.CASCADE, null=True, blank=True,validators=[ RegexValidator(regex='^[A-Za-z\s]+$',message='Use apenas letras e espaços.')])
    instituicao = models.ForeignKey(Instituicao, on_delete=models.CASCADE, null=True, blank=True,validators=[ RegexValidator(regex='^[A-Za-z\s]+$',message='Use apenas letras e espaços.')])

    def __str__(self):
        return f'{self.area} - {self.status}'


class ImportTermoEstagio(models.Model):
    file = models.FileField(upload_to='termo_estagio/%Y/%m/%d/')

    def __str__(self):
        return f'{self.file}'
