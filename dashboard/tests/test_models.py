from django.test import TestCase
from dashboard.models import (
    Endereco,
    Instituicao,
    CoordenadorExtensao,
    Empresa,
    Cursos,
    Estagiario,
    Supervisor,
    Estagio,
    ImportTermoEstagio,
)
from django.core.exceptions import ValidationError
from datetime import timedelta, date


class TestModels(TestCase):

    def test_criar_endereco(self):
        endereco = Endereco.objects.create(
            rua="Rua Teste",
            numero="123",
            bairro="Centro",
            cidade="Cidade Teste",
            estado="Estado Teste",
            cep="12345678",
        )
        self.assertEqual(endereco.rua, "Rua Teste")
        self.assertEqual(endereco.numero, "123")

    def test_criar_instituicao(self):
        endereco = Endereco.objects.create(
            rua="Rua Teste",
            numero="123",
            bairro="Centro",
            cidade="Cidade Teste",
            estado="Estado Teste",
            cep="12345678",
        )
        instituicao = Instituicao.objects.create(
            cnpj="12345678000199",
            nome="Instituição Teste",
            email="instituicao@test.com",
            telefone="1234567890",
        )
        self.assertEqual(instituicao.nome, "Instituição Teste")
        self.assertEqual(instituicao.cnpj, "12345678000199")

    def test_criar_empresa(self):
        endereco = Endereco.objects.create(
            rua="Rua Teste",
            numero="123",
            bairro="Centro",
            cidade="Cidade Teste",
            estado="Estado Teste",
            cep="12345678",
        )
        instituicao = Instituicao.objects.create(
            cnpj="12345678000199",
            nome="Instituição Teste",
            email="instituicao@test.com",
            telefone="1234567890",
            endereco=endereco,
        )
        empresa = Empresa.objects.create(
            empresa_nome="Empresa Teste",
            cnpj="12345678000199",
            razao_social="Razão Social Teste",
            email="empresa@test.com",
            instituicao=instituicao,
        )
        self.assertEqual(empresa.empresa_nome, "Empresa Teste")
        self.assertEqual(empresa.cnpj, "12345678000199")

    def test_criar_cursos(self):
        instituicao = Instituicao.objects.create(
            cnpj="12345678000199",
            nome="Instituição Teste",
            email="instituicao@test.com",
            telefone="1234567890",
        )
        curso = Cursos.objects.create(
            instituicao=instituicao,
            nome_curso="Curso Teste",
            descricao="Descrição Teste",
            area="Tecnologia",
            coordenador="Coordenador Teste",
            email_coordenador="coordenador@test.com",
        )
        self.assertEqual(curso.nome_curso, "Curso Teste")

    def test_criar_estagiario(self):
        instituicao = Instituicao.objects.create(
            cnpj="12345678000199",
            nome="Instituição Teste",
            email="instituicao@test.com",
            telefone="1234567890",
        )
        curso = Cursos.objects.create(
            instituicao=instituicao,
            nome_curso="Curso Teste",
            descricao="Descrição Teste",
            area="Tecnologia",
            coordenador="Coordenador Teste",
            email_coordenador="coordenador@test.com",
        )
        estagiario = Estagiario.objects.create(
            primeiro_nome="Estagiário",
            sobrenome="Teste",
            cpf="12345678901",
            matricula="123456",
            email="estagiario@test.com",
            telefone="1234567890",
            curso=curso,
            status=False,
        )
        self.assertEqual(estagiario.primeiro_nome, "Estagiário")

    def test_criar_supervisor(self):
        endereco = Endereco.objects.create(
            rua="Rua Teste",
            numero="123",
            bairro="Centro",
            cidade="Cidade Teste",
            estado="Estado Teste",
            cep="12345678",
        )
        instituicao = Instituicao.objects.create(
            cnpj="12345678000199",
            nome="Instituição Teste",
            email="instituicao@test.com",
            telefone="1234567890",
            endereco=endereco,
        )
        empresa = Empresa.objects.create(
            empresa_nome="Empresa Teste",
            cnpj="12345678000199",
            razao_social="Razão Social Teste",
            email="empresa@test.com",
            instituicao=instituicao,
        )
        supervisor = Supervisor.objects.create(
            cpf="12345678901",
            email="supervisor@test.com",
            telefone="1234567890",
            primeiro_nome="Supervisor",
            sobrenome="Teste",
            cargo="Cargo Teste",
            empresa=empresa,
        )
        self.assertEqual(supervisor.primeiro_nome, "Supervisor")

    def test_criar_estagio(self):
        instituicao = Instituicao.objects.create(
            cnpj="12345678000199",
            nome="Instituição Teste",
            email="instituicao@test.com",
            telefone="1234567890",
        )
        empresa = Empresa.objects.create(
            empresa_nome="Empresa Teste",
            cnpj="12345678000199",
            razao_social="Razão Social Teste",
            email="empresa@test.com",
            instituicao=instituicao,
        )
        estagiario = Estagiario.objects.create(
            primeiro_nome="Estagiário",
            sobrenome="Teste",
            cpf="12345678901",
            matricula="123456",
            email="estagiario@test.com",
            telefone="1234567890",
        )
        estagio = Estagio.objects.create(
            area="Desenvolvimento",
            tipo_estagio="Não obrigatório",
            status="Em andamento",
            descricao="Estágio Teste",
            data_inicio=date.today(),
            data_fim=date.today() + timedelta(days=30),
            estagiario=estagiario,
            empresa=empresa,
            instituicao=instituicao,
        )
        self.assertEqual(estagio.area, "Desenvolvimento")

    def test_import_termo_estagio_criar(self):
        import_termo = ImportTermoEstagio.objects.create(file="termo_estagio/test.pdf")
        self.assertTrue(import_termo.file.name.endswith(".pdf"))
