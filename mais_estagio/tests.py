from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import (
    Endereco,
    Instituicao,
    CoordenadorExtensao,
    Empresa,
    Cursos,
    Aluno,
    Supervisor,
    Estagio,
)
from django.urls import reverse


class ViewsIntegrationTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.endereco = Endereco.objects.create(
            rua="Rua Exemplo",
            numero="123",
            bairro="Centro",
            cidade="Cidade X",
            estado="Estado Y",
            cep="12345678",
        )

        self.instituicao = Instituicao.objects.create(
            cnpj="12345678901234",
            nome="Instituição X",
            email="instituicao@example.com",
            telefone="11987654321",
            endereco=self.endereco,
        )

        self.user = User.objects.create_user(
            username="coordenador", password="senha123"
        )

        self.coordenador = CoordenadorExtensao.objects.create(
            user=self.user,
            cpf="12345678901",
            email="coord@example.com",
            nome_completo="João da Silva",
            instituicao=self.instituicao,
        )

        self.empresa = Empresa.objects.create(
            instituicao=self.instituicao,
            nome="Empresa Teste",
            cnpj="98765432109876",
            razao_social="Empresa Teste Ltda",
            email="empresa@example.com",
            atividades="Atividades de teste",
            endereco=self.endereco,
        )

        self.curso = Cursos.objects.create(
            instituicao=self.instituicao,
            nome_curso="Ciência da Computação",
            descricao="Curso de TI",
            area="Tecnologia",
            coordenador="Maria",
            email_coordenador="maria@example.com",
        )

        self.estagiario = Aluno.objects.create(
            nome_completo="Carlos Sousa",
            cpf="98765432101",
            matricula="2023123456",
            email="carlos@example.com",
            telefone="11999999999",
            curso=self.curso,
            status=True,
            endereco=self.endereco,
            instituicao=self.instituicao,
        )

    def test_home_view(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/home.html")

    def test_dashboard_view_authenticated(self):
        self.client.login(username="coordenador", password="senha123")
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dashboard.html")

    def test_dashboard_cursos_view(self):
        self.client.login(username="coordenador", password="senha123")
        response = self.client.get(reverse("dashboard_cursos"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ciência da Computação")

    def test_dashboard_empresa_view(self):
        self.client.login(username="coordenador", password="senha123")
        response = self.client.get(reverse("dashboard_empresa"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Empresa Teste")

    def test_dashboard_estagiario_view(self):
        self.client.login(username="coordenador", password="senha123")
        response = self.client.get(reverse("dashboard_estagiario"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Carlos Souza")

    def test_dashboard_instituicao_view_login_required(self):
        response = self.client.get(reverse("dashboard_instituicao"))
        self.assertEqual(response.status_code, 302)  # Redireciona para login

    def test_dashboard_instituicao_view_authenticated(self):
        self.client.login(username="coordenador", password="senha123")
        response = self.client.get(reverse("dashboard_instituicao"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Instituição X")


class IntegracaoModelsTestCase(TestCase):
    def setUp(self):
        self.endereco = Endereco.objects.create(
            rua="Rua Exemplo",
            numero="123",
            bairro="Centro",
            cidade="Cidade X",
            estado="Estado Y",
            cep="12345678",
        )

        self.instituicao = Instituicao.objects.create(
            cnpj="12345678901234",
            nome="Instituição X",
            email="instituicao@example.com",
            telefone="11987654321",
            endereco=self.endereco,
        )

        self.user = User.objects.create_user(
            username="coordenador", password="senha123"
        )

        self.coordenador = CoordenadorExtensao.objects.create(
            user=self.user,
            cpf="12345678901",
            email="coord@example.com",
            nome_completo="João da Silva",
            instituicao=self.instituicao,
        )

        self.empresa = Empresa.objects.create(
            instituicao=self.instituicao,
            nome="Empresa Teste",
            cnpj="98765432109876",
            razao_social="Empresa Teste Ltda",
            email="empresa@example.com",
            atividades="Atividades de teste",
            endereco=self.endereco,
        )

        self.curso = Cursos.objects.create(
            instituicao=self.instituicao,
            nome_curso="Ciência da Computação",
            descricao="Curso de TI",
            area="Tecnologia",
            coordenador="Maria",
            email_coordenador="maria@example.com",
        )

        self.estagiario = Aluno.objects.create(
            nome_completo="Carlos da Silva",
            cpf="98765432101",
            matricula="2023123456",
            email="carlos@example.com",
            telefone="11999999999",
            curso=self.curso,
            status=True,
            endereco=self.endereco,
            instituicao=self.instituicao,
        )

        self.supervisor = Supervisor.objects.create(
            nome_completo="Roberto Santos",
            cpf="32165498701",
            email="roberto@example.com",
            telefone="11888888888",
            cargo="Gerente",
            empresa=self.empresa,
        )

        self.estagio = Estagio.objects.create(
            bolsa_estagio=1200.00,
            area="TI",
            tipo_estagio="Obrigatório",
            status="Em andamento",
            descricao="Estágio na área de TI",
            data_inicio="2024-01-10",
            data_fim="2024-07-10",
            turno="Manha",
            auxilio_transporte=300.00,
            estagiario=self.estagiario,
            empresa=self.empresa,
            supervisor=self.supervisor,
            instituicao=self.instituicao,
            orientador="Professor X",
        )

    def test_criacao_endereco(self):
        self.assertEqual(self.endereco.cidade, "Cidade X")

    def test_criacao_instituicao(self):
        self.assertEqual(self.instituicao.nome, "Instituição X")

    def test_criacao_coordenador(self):
        self.assertEqual(self.coordenador.nome_completo, "João da Silva")

    def test_criacao_empresa(self):
        self.assertEqual(self.empresa.nome, "Empresa Teste")

    def test_criacao_curso(self):
        self.assertEqual(self.curso.nome_curso, "Ciência da Computação")

    def test_criacao_estagiario(self):
        self.assertEqual(self.estagiario.email, "carlos@example.com")

    def test_criacao_estagio(self):
        self.assertEqual(self.estagio.descricao, "Estágio na área de TI")
