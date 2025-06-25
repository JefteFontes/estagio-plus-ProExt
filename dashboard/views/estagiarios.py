from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator

from dashboard.models import Cursos, Endereco, Instituicao, Aluno
from home.utils import validate_cpf



from dashboard.models import CoordenadorExtensao, Estagio
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
def editar_estagiario(request, estagiario_id):
    estagiario = get_object_or_404(Aluno, id=estagiario_id)
    coordenador = CoordenadorExtensao.objects.get(user=request.user)

    if request.method == "POST":
        form = EstagiarioCadastroForm(
            request.POST, instance=estagiario, coordenador=coordenador
        )
        if form.is_valid():
            form.save()
            return redirect("dashboard_estagiario")

    form = EstagiarioCadastroForm(instance=estagiario, coordenador=coordenador)
    return render(
        request, "cadastrar_estagiario.html", {"form": form, "estagiario": estagiario}
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
            return redirect("dashboard_estagiario")
    else:
        form = EstagiarioCadastroForm(
            initial={"email": invite.email}, instituicao=invite.instituicao
        )
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

    class Meta:
        model = Aluno
        fields = [
            "nome",
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
            "nome": forms.TextInput(
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
