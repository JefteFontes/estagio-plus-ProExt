from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator

from mais_estagio.models import Cursos, Endereco, Instituicao, Aluno, SexoChoices
from home.utils import validate_cpf

from django.utils import timezone
from datetime import date, timedelta


from mais_estagio.models import CoordenadorExtensao, Estagio
from ..forms import EstagiarioCadastroForm, Aluno


@login_required
def cadastrar_estagiario(request):
    coordenador = CoordenadorExtensao.objects.get(user=request.user)
    if request.method == "POST":
        form = EstagiarioCadastroForm(coordenador=coordenador, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Estágiario cadastrado com sucesso!")
            return redirect("dashboard_estagiario")

    form = EstagiarioCadastroForm(coordenador=coordenador)

    return render(request, "cadastrar_estagiario.html", {"form": form})

@login_required
@login_required
def editar_estagiario(request, estagiario_id):
    estagiario_instance = get_object_or_404(Aluno, id=estagiario_id)
    
    template_name = "cadastrar_estagiario.html"

    if hasattr(request.user, "aluno") and request.user.aluno:
        if estagiario_instance != request.user.aluno:
            messages.error(request, "Você não tem permissão para editar este perfil.")
            return redirect('estagio_andamento')
        else:
            template_name = "aluno/editar_perfil.html"
            form_kwargs = {'instance': estagiario_instance}
    else:
        if not (hasattr(request.user, "coordenadorextensao") and request.user.coordenadorextensao):
            messages.error(request, "Você não tem permissão para acessar esta página.")
            return redirect('home')

        coordenador = request.user.coordenadorextensao
        form_kwargs = {'instance': estagiario_instance, 'coordenador': coordenador}


    if request.method == "POST":
        form = EstagiarioCadastroForm(request.POST, **form_kwargs)
        if form.is_valid():
            form.save()
            messages.success(request, "Dados atualizados com sucesso!")
            
            if hasattr(request.user, "aluno") and request.user.aluno and estagiario_instance == request.user.aluno:
                return redirect("estagio_andamento")
            else:
                return redirect("dashboard_instituicao")
        else:
            messages.error(request, "Erro ao atualizar dados. Verifique o formulário.")

    form = EstagiarioCadastroForm(**form_kwargs)
    
    return render(
        request, template_name, {"form": form, "estagiario": estagiario_instance}
    )

@login_required
def deletar_estagiario(request, estagiario_id):
    estagiario = get_object_or_404(Aluno, id=estagiario_id)
    # verificar se der algum erro
    if Estagio.objects.filter(estagiario=estagiario).exists():
        messages.error(
            request, "O estagiario possui estagios vinculados e nao pode ser deletado."
        )
        return redirect("dashboard_estagiario")
    else:
        estagiario.delete()
        return redirect("dashboard_estagiario")


def estagiario_auto_cadastro(request, token):
    invite = get_object_or_404(token=token, used=False)
    if request.method == "POST":
        form = EstagiarioCadastroForm(data=request.POST, instituicao=invite.instituicao)
        if form.is_valid():
            estagiario = form.save(commit=False)
            estagiario.instituicao = invite.instituicao
            estagiario.save()
            invite.used = True
            invite.save()
            messages.success(request, "Cadastro realizado com sucesso!")
            return redirect('dashboard_estagiario')
    else:
        form = EstagiarioCadastroForm(initial={'email': invite.email}, instituicao=invite.instituicao)
    return render(request, "cadastrar_estagiario.html", {"form": form})


class AlunoCadastroForm(forms.ModelForm):
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
    data_nascimento = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "class": "form-control",
                "type": "date",
                "max": (date.today() - timedelta(days=365*14)).strftime("%Y-%m-%d"),  # 14 anos atrás
                "min": date(1900, 1, 1).strftime("%Y-%m-%d")  # Data mínima
            }
        ),
        validators=[
            MinValueValidator(
                limit_value=date(1900, 1, 1),
                message="Data de nascimento não pode ser anterior a 01/01/1900"
            ),
            MaxValueValidator(
                limit_value=date.today() - timedelta(days=365*14),
                message="O aluno deve ter pelo menos 14 anos de idade"
            )
        ]
    )

    class Meta:
        model = Aluno
        fields = [
            "nome_completo",
            "cpf",
            "matricula",
            "telefone",
            "email",
            "sexo",
            "data_nascimento",
            "curso",
            "periodo",
            "turno",
            "ira",
            "instituicao",
        ]
        widgets = {
            "nome_completo": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nome Completo (ex: João da Silva)"}
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
            "sexo": forms.Select(attrs={"class": "form-control"}),
            "data_nascimento": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                    "max": (date.today() - timedelta(days=365*14)).strftime("%Y-%m-%d"),
                    "min": date(1900, 1, 1).strftime("%Y-%m-%d")
                }
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

        aluno = super().save(commit=False)
        aluno.endereco = endereco
        aluno.status = False  
        if commit:
            aluno.save()
        return aluno
