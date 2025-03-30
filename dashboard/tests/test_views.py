from django.test import TestCase, RequestFactory
from django.http import JsonResponse
from dashboard.models import CoordenadorExtensao, Estagiario, Estagio
from unittest.mock import patch
from django.urls import reverse
from django.contrib.auth.models import User
import requests_mock
from ..views import buscar_cep
import json
from dashboard.views.utils import validate_cpf
from django.contrib.messages import get_messages
from dashboard.models import *

class BuscarCepTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @requests_mock.Mocker()

    def test_buscar_cep_valido(self, mock_request):
        mock_response_data = {
            "logradouro": "Estrada dos Bambus",
            "bairro": "Mombaça",
            "localidade": "Saquarema",
            "uf": "RJ",
            "cep": "28990-001"
        }

        mock_request.get("https://viacep.com.br/ws/28990001/json/", json=mock_response_data)
        request = self.factory.get("/buscar_cep?cep=28990-001")

        response = buscar_cep(request)
        self.assertIsInstance(response, JsonResponse)
        response_data = json.loads(response.content)

        self.assertEqual(response_data["logradouro"], "Estrada dos Bambus")
        self.assertEqual(response_data["bairro"], "Mombaça")
        self.assertEqual(response_data["cidade"], "Saquarema")
        self.assertEqual(response_data["estado"], "RJ")


    def test_buscar_cep_invalido(self):

        request = self.factory.get("/buscar_cep?cep=123")
        response = buscar_cep(request)
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertEqual(response_data["error"], "CEP inválido")

    @requests_mock.Mocker()
    def test_buscar_cep_nao_encontrado(self, mock_request):
    
        mock_request.get("https://viacep.com.br/ws/00000000/json/", json={"erro": True}, status_code=200)
        request = self.factory.get("/buscar_cep?cep=00000000")
        response = buscar_cep(request)
        self.assertEqual(response.status_code, 404)
        response_data = json.loads(response.content)
        self.assertEqual(response_data["error"], "CEP não encontrado")


class ValidoCPFTest(TestCase):

    def test_valido_cpf(self):
        cpf_valido = "123.456.789-09"
        self.assertTrue(validate_cpf(cpf_valido))

    def test_invalido_cpf_tamanho(self):
        cpf_invalido = "123.456.78"
        self.assertFalse(validate_cpf(cpf_invalido))

    def test_invalido_cpf_iguais(self):
        cpf_invalido = "111.111.111-11"
        self.assertFalse(validate_cpf(cpf_invalido))

    def test_invalido_cpf_digitos_invalidos(self):
        cpf_invalido = "123.456.789-00"
        self.assertFalse(validate_cpf(cpf_invalido))

    def test_valido_cpf_com__caracteres_não_numericos(self):
        cpf_valido = "123.456.789-09"
        self.assertTrue(validate_cpf(cpf_valido))

    def test_invalido_cpf_com__caracteres_não_numericos(self):
        cpf_invalido = "123-456-789/00"
        self.assertFalse(validate_cpf(cpf_invalido))



class EstagiarioViewTests(TestCase):

    def setUp(self):
        
        self.user = User.objects.create_user(username='coordenador', password='senha')
        self.coordenador = CoordenadorExtensao.objects.create(
            user=self.user,
            cpf='12345678901',
            email='coordenador@test.com',
            primeiro_nome='Coord',
            sobrenome='Test'
        )
        
        self.instituicao = Instituicao.objects.create(
            cnpj="12345678000199",
            nome="Instituição Teste",
            email="instituicao@test.com",
            telefone="1234567890"
        )
        self.curso = Cursos.objects.create(
            instituicao=self.instituicao,
            nome_curso="Curso Teste",
            descricao="Descrição do curso",
            area="Tecnologia",
            coordenador="Coordenador Teste",
            email_coordenador="coordenador@test.com"
        )
        self.url_cadastrar = reverse('cadastrar_estagiario')
        self.url_dashboard = reverse('dashboard_estagiario')
        self.estagiario = Estagiario.objects.create(
            primeiro_nome="João",
            sobrenome="Silva",
            cpf="11122233344",
            matricula="123456",
            email="joao.silva@test.com",
            telefone="1234567890",
            curso=self.curso
        )

    def test_cadastrar_estagiario_get(self):
        self.client.login(username='coordenador', password='senha')
        response = self.client.get(self.url_cadastrar)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cadastrar_estagiario.html')

    def test_cadastrar_estagiario_post_successo(self):
        self.client.login(username='coordenador', password='senha')
        data = {
            # Dados do estagiário
            'primeiro_nome': 'Carlos',
            'sobrenome': 'Almeida',
            'cpf': '98765432100',
            'matricula': '654321',
            'email': 'carlos.almeida@test.com',
            'telefone': '9876543210',
            'rua': 'Rua X',
            'numero': '100',
            'bairro': 'Centro',
            'cidade': 'CidadeX',
            'estado': 'EstadoX',
            'cep': '12345678',
            'complemento': '',
            'curso': self.curso.id,
            'status': False,
        }
        response = self.client.post(self.url_cadastrar, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.url_dashboard)
        self.assertTrue(Estagiario.objects.filter(cpf='98765432100').exists())

    def test_cadastrar_estagiario_post_invalido(self):
        self.client.login(username='coordenador', password='senha')
        data = {
            'primeiro_nome': '',  
            'sobrenome': 'Almeida',
            'cpf': '98765432100',
            'matricula': '654321',
            'email': 'carlos.almeida@test.com',
            'telefone': '9876543210',
            'rua': 'Rua X',
            'numero': '100',
            'bairro': 'Centro',
            'cidade': 'CidadeX',
            'estado': 'EstadoX',
            'cep': '12345678',
            'complemento': '',
            'curso': self.curso.id,
            'status': False,
        }
        response = self.client.post(self.url_cadastrar, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Este campo é obrigatório.')

    def test_editar_estagiario_get(self):
        self.client.login(username='coordenador', password='senha')
        url_editar = reverse('editar_estagiario', args=[self.estagiario.id])
        response = self.client.get(url_editar)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cadastrar_estagiario.html')


    def test_deletar_estagiario_com_estagio(self):
        self.client.login(username='coordenador', password='senha')
        estagio = Estagio.objects.create(
            estagiario=self.estagiario,
            empresa=None,
            instituicao=None,
            tipo_estagio='Não obrigatório',
            status='Em andamento',
            data_inicio='2025-01-01',
            data_fim='2025-02-01'
        )
        url_deletar = reverse('deletar_estagiario', args=[self.estagiario.id])
        response = self.client.post(url_deletar, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'O estagiario possui estagios vinculados e nao pode ser deletado.')
        self.assertTrue(Estagiario.objects.filter(id=self.estagiario.id).exists())

    def test_deletar_estagiario_sem_estagio(self):
        self.client.login(username='coordenador', password='senha')
        url_deletar = reverse('deletar_estagiario', args=[self.estagiario.id])
        response = self.client.post(url_deletar)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.url_dashboard)
        self.assertFalse(Estagiario.objects.filter(id=self.estagiario.id).exists())
