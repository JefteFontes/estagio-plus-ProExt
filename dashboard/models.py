from django.db import models


class Endereco(models.Model):
    rua = models.CharField(max_length=255)
    numero = models.CharField(max_length=10)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=50)
    cep = models.CharField(max_length=20)

    def __str__(self):
        return f'{self.rua}, {self.numero} - {self.bairro}'


class Empresa(models.Model):
    nome = models.CharField(max_length=250)
    cnpj = models.CharField(max_length=250)
    razao_social = models.CharField(max_length=250)
    email = models.EmailField(unique=True)
    endereco = models.ForeignKey(Endereco, on_delete=models.CASCADE)

    def __str__(self):
        return self.nome


class Instituicao(models.Model):
    cnpj = models.CharField(max_length=20)
    nome = models.CharField(max_length=250)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20)
    endereco = models.ForeignKey(Endereco, on_delete=models.CASCADE)

    def __str__(self):
        return self.nome


class Estagiario(models.Model):
    primeiro_nome = models.CharField(max_length=250)
    sobrenome = models.CharField(max_length=250)
    cpf = models.CharField(max_length=12)
    matricula = models.CharField(max_length=55)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20)
    curso = models.CharField(max_length=55)
    status = models.BooleanField()
    endereco = models.ForeignKey(Endereco, on_delete=models.CASCADE)
    instituicao = models.ForeignKey(Instituicao, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.primeiro_nome} {self.sobrenome}'


class CoordenadorExtensao(models.Model):
    cpf = models.CharField(max_length=12)
    email = models.EmailField(unique=True)
    primeiro_nome = models.CharField(max_length=250)
    sobrenome = models.CharField(max_length=250)
    instituicao = models.ForeignKey(Instituicao, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.primeiro_nome} {self.sobrenome}'


class Supervisor(models.Model):
    cpf = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20)
    primeiro_nome = models.CharField(max_length=250)
    sobrenome = models.CharField(max_length=250)
    cargo = models.CharField(max_length=254)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.primeiro_nome} {self.sobrenome}'


class Estagio(models.Model):
    bolsa_estagio = models.FloatField(blank=True)
    area = models.CharField(max_length=250)
    status = models.BooleanField()
    descricao = models.TextField()
    data_inicio = models.DateField()
    data_fim = models.DateField()
    turno = models.CharField(max_length=30)
    estagiario = models.ForeignKey(Estagiario, on_delete=models.CASCADE)
    supervisor = models.ForeignKey(Supervisor, on_delete=models.CASCADE)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    instituicao = models.ForeignKey(Instituicao, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.area} - {self.status}'
