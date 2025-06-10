import re
from django import forms
from django.contrib.auth.models import User
from dashboard.models import CoordenadorExtensao, Instituicao, Endereco, Aluno, Cursos
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
        coordenador.user = user  # Certifica-se de associar o usuário antes de salvar

        if commit:
            user.save()
            coordenador.save()

        return user, coordenador


class AlunoCadastroForm(forms.ModelForm):

    # Campos de endereço
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
            attrs={"class": "form-control", "placeholder": "Cidade (ex: Parnaíba)"}
        ),
    )
    estado = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Estado (ex: PI)"}
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
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Complemento"}
        ),
    )

    ira = forms.FloatField(
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": "IRA (ex: 7.5)",
                "step": "0.1",
                "min": "0",
                "max": "10",
            }
        ),
        validators=[
            MinValueValidator(0.0, message="O IRA não pode ser menor que 0.0"),
            MaxValueValidator(10.0, message="O IRA não pode ser maior que 10.0"),
        ],
    )

    instituicao = forms.ModelChoiceField(
        queryset=Instituicao.objects.all(),
        widget=forms.Select(attrs={"class": "form-control", "id": "id_instituicao"}),
        empty_label="Selecione a instituição",
    )

    class Meta:
        model = Aluno
        fields = [
            "nome_completo",
            "cpf",
            "matricula",
            "telefone",
            "email",
            "curso",
            "periodo",
            "turno",
            "ira",
            "instituicao",
        ]
        widgets = {
            "nome_completo": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nome completo"}
            ),
            "cpf": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "CPF"}
            ),
            "matricula": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Matrícula"}
            ),
            "telefone": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Telefone"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "Email"}
            ),
            "curso": forms.Select(attrs={"class": "form-control", "id": "id_curso"}),
            "periodo": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Período",
                    "min": 1,
                    "max": 8,
                }
            ),
            "turno": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Se uma instituição foi selecionada, filtra os cursos
        if "instituicao" in self.data:
            try:
                instituicao_id = int(self.data.get("instituicao"))
                self.fields["curso"].queryset = Cursos.objects.filter(
                    instituicao_id=instituicao_id
                )
            except (ValueError, TypeError):
                self.fields["curso"].queryset = Cursos.objects.none()
        elif self.instance.pk:
            self.fields["curso"].queryset = Cursos.objects.filter(
                instituicao=self.instance.instituicao
            )
        else:
            self.fields["curso"].queryset = Cursos.objects.none()

    def clean_cpf(self):
        cpf = self.cleaned_data.get("cpf", "")
        cpf = "".join(filter(str.isdigit, cpf))
        if not validate_cpf(cpf):
            raise forms.ValidationError("CPF inválido")
        return cpf

    def save(self, commit=True):
        endereco_data = {
            "rua": self.cleaned_data["rua"],
            "numero": self.cleaned_data["numero"],
            "bairro": self.cleaned_data["bairro"],
            "cidade": self.cleaned_data["cidade"],
            "estado": self.cleaned_data["estado"],
            "cep": self.cleaned_data["cep"],
            "complemento": self.cleaned_data["complemento"],
        }
        endereco = Endereco.objects.create(**endereco_data)

        estagiario = super().save(commit=False)
        estagiario.endereco = endereco
        estagiario.status = False  # Marcado como pendente para validação
        if commit:
            estagiario.save()
        return estagiario
