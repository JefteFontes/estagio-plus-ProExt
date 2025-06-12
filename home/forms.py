import re
from django import forms
from django.contrib.auth.models import User
from aluno.models import Aluno
from dashboard.models import CoordenadorExtensao, Instituicao, Endereco, Cursos
from dashboard.views.utils import validate_cpf
from django.core.validators import MinValueValidator, MaxValueValidator


class CoordenadorCadastroForm(forms.ModelForm):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "exemplo@dominio.com"}
        )
    )
    rua = forms.CharField(
        max_length=255,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Rua das Flores"}
        ),
    )
    numero = forms.CharField(
        max_length=10,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Número (ex: 123)"}
        ),
    )
    bairro = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Bairro (ex: Centro)"}
        ),
    )
    cidade = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Cidade (ex: São Paulo)"}
        ),
    )
    estado = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Estado (ex: SP)"}
        ),
    )
    cep = forms.CharField(
        max_length=20,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "CEP (ex: 12345-678)"}
        ),
    )
    complemento = forms.CharField(
        max_length=200,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Complemento"}
        ),
        required=False,
    )
    instituicao_nome = forms.CharField(
        max_length=250,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Nome da Instituição (ex: Universidade XYZ)",
            }
        ),
    )
    instituicao_cnpj = forms.CharField(
        max_length=20,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "CNPJ (ex: 12.345.678/0001-90)",
            }
        ),
    )
    instituicao_telefone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Telefone (ex: 86 1234-5678)",
            }
        ),
    )
    instituicao_logo = forms.ImageField(
        label="Logo da instituição",
        widget=forms.ClearableFileInput(attrs={"class": "form-control"}),
        required=False,
    )

    class Meta:
        model = CoordenadorExtensao
        fields = ["nome_completo", "cpf"]
        widgets = {
            "nome_completo": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nome Completo (ex: João da Silva)",
                }
            ),
            "cpf": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "CPF (ex: 12345678900)"}
            ),
        }

    def clean_cpf(self):
        cpf = self.cleaned_data["cpf"]
        cpf = re.sub(r"\D", "", cpf)  # Remove tudo que não for número

        if not validate_cpf(cpf):  # Valida CPF depois de limpar
            raise forms.ValidationError(
                "CPF inválido. Use um CPF válido com 11 dígitos."
            )

        return cpf

    def save(self, commit=True):
        user_data = {
            "username": f"{self.cleaned_data['nome_completo']}",
            "email": self.cleaned_data["email"],
        }

        if User.objects.filter(email=self.cleaned_data["email"]).exists():
            raise forms.ValidationError("Já existe um usuário com este e-mail.")

        password = self.clean_cpf()

        user = User.objects.create_user(**user_data, password=password)

        endereco = Endereco.objects.create(
            rua=self.cleaned_data["rua"],
            numero=self.cleaned_data["numero"],
            bairro=self.cleaned_data["bairro"],
            cidade=self.cleaned_data["cidade"],
            estado=self.cleaned_data["estado"],
            cep=self.cleaned_data["cep"],
            complemento=self.cleaned_data["complemento"],
        )

        instituicao = Instituicao.objects.create(
            nome=self.cleaned_data["instituicao_nome"],
            cnpj=self.cleaned_data["instituicao_cnpj"],
            telefone=self.cleaned_data["instituicao_telefone"],
            email=self.cleaned_data["email"],
            logo=self.cleaned_data.get("instituicao_logo"),
            endereco=endereco,
        )

        coordenador = super().save(commit=False)
        coordenador.instituicao = instituicao
        coordenador.email = self.cleaned_data["email"]
        coordenador.user = user  

        if commit:
            user.save()
            coordenador.save()

        return user, coordenador



