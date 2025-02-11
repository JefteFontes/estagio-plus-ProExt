from django import forms
from django.contrib.auth.models import User
from .views.utils import validate_cpf, validate_cnpj
from .models import (
    Estagiario,
    Endereco,
    Estagio,
    Supervisor,
    Empresa,
    Instituicao,
    TurnoChoices,
    StatusChoices,  
    Areachoices,
    Cursos,
    CoordenadorExtensao,
)


class CursosCadastroForm(forms.ModelForm):
    class Meta:
        model = Cursos
        fields = ["nome_curso", "descricao", "area", "coordenador", "email_coordenador"]
        widgets = {
            "nome_curso": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nome do Curso"}
            ),
            "descricao": forms.Textarea(
                attrs={"class": "form-control", "placeholder": "Descrição"}
            ),
            "area": forms.Select(attrs={"class": "form-control"}),
            "coordenador": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Coordenador"}
            ),
            "email_coordenador": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "E-mail"}
            ),
        }

    def __init__(self, *args, **kwargs):
        # Remover 'coordenador_extensao' de kwargs para passá-lo manualmente
        self.coordenador_extensao = kwargs.pop("coordenador_extensao", None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        # Criação do objeto 'cursos'
        cursos = super().save(commit=False)

        # Se o coordenador_extensao foi passado, atribui a instituição
        if self.coordenador_extensao:
            cursos.instituicao = self.coordenador_extensao.instituicao

        if commit:
            cursos.save()
        return cursos


class EstagioCadastroForm(forms.ModelForm):
    bolsa_estagio = forms.FloatField(
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "Bolsa de Estágio"})
    )
    area = forms.ChoiceField(
        choices=Areachoices.choices, widget=forms.Select(attrs={"class": "form-select"})
    )
    status = forms.ChoiceField(
        choices=StatusChoices.choices, widget=forms.Select(attrs={"class": "form-select"})
    )
    descricao = forms.CharField(
        max_length=255,
        widget=forms.Textarea(attrs={"class": "form-control", "placeholder": "Descrição", "rows": 4, "cols": 50})
    )
    auxilio_transporte = forms.FloatField(
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "Auxílio de Transporte"})
    )
    data_inicio = forms.DateField(
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date", "placeholder": "Data de Início"})
    )
    data_fim = forms.DateField(
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date", "placeholder": "Data de Fim"})
    )
    turno = forms.ChoiceField(
        choices=TurnoChoices.choices, widget=forms.Select(attrs={"class": "form-select"})
    )
    estagiario = forms.ModelChoiceField(
        queryset=Estagiario.objects.all(), widget=forms.Select(attrs={"class": "form-select"})
    )
    empresa = forms.ModelChoiceField(
        queryset=Empresa.objects.all(), widget=forms.Select(attrs={"class": "form-select", "id": "empresa-select"})
    )
    supervisor = forms.ModelChoiceField(
        queryset=Supervisor.objects.none(), widget=forms.Select(attrs={"class": "form-select", "id": "supervisor-select"}), required=False
    )
    instituicao = forms.ModelChoiceField(
        queryset=Instituicao.objects.all(), widget=forms.Select(attrs={"class": "form-select"})
    )

    class Meta:
        model = Estagio
        fields = [
            "bolsa_estagio", "auxilio_transporte", "area", "status", "descricao",
            "data_inicio", "data_fim", "turno", "estagiario", "empresa", "supervisor", "instituicao"
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["empresa"].queryset = Empresa.objects.all()
        empresa_id = self.data.get("empresa") or (self.instance.empresa.id if self.instance.pk else None)
        if empresa_id:
            self.fields["supervisor"].queryset = Supervisor.objects.filter(empresa_id=empresa_id)
        else:
            self.fields["supervisor"].queryset = Supervisor.objects.all()

    def save(self, commit=True):
        estagio = super().save(commit=False)
        if commit:
            estagio.save()
        return estagio


class EstagiarioCadastroForm(forms.ModelForm):
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

    def clean_cpf(self):
        cpf = self.cleaned_data["cpf"]
        cpf = ''.join(filter(str.isdigit, cpf))
        if not validate_cpf(cpf):
            raise forms.ValidationError("CPF inválido")
        return cpf

    class Meta:
        model = Estagiario
        fields = [
            "primeiro_nome",
            "sobrenome",
            "cpf",
            "matricula",
            "telefone",
            "curso",
            "status",
            "email",
        ]
        widgets = {
            "primeiro_nome": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Primeiro Nome (ex: João)",
                }
            ),
            "sobrenome": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Sobrenome (ex: Silva)"}
            ),
            "cpf": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "CPF (ex: 12345678900)"}
            ),
            "matricula": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Matrícula (ex: 202312345)",
                }
            ),
            "telefone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Telefone (ex: 11 91234-5678)",
                }
            ),
            "curso": forms.Select(attrs={"class": "form-control"}),
            "status": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "exemplo@dominio.com"}
            ),
        }

    def __init__(self, *args, **kwargs):
        self.coordenador = kwargs.pop("coordenador", None)
        super().__init__(*args, **kwargs)
         # Preenche os campos de endereço, caso o estagiário já tenha um endereço associado
        if self.instance and self.instance.pk and self.instance.endereco:
            endereco = self.instance.endereco
            self.fields['rua'].initial = endereco.rua
            self.fields['numero'].initial = endereco.numero
            self.fields['bairro'].initial = endereco.bairro
            self.fields['cidade'].initial = endereco.cidade
            self.fields['estado'].initial = endereco.estado
            self.fields['cep'].initial = endereco.cep
            self.fields['complemento'].initial = endereco.complemento

    def save(self, commit=True):
        # Salva ou atualiza o endereço
        endereco_data = {
            'rua': self.cleaned_data['rua'],
            'numero': self.cleaned_data['numero'],
            'bairro': self.cleaned_data['bairro'],
            'cidade': self.cleaned_data['cidade'],
            'estado': self.cleaned_data['estado'],
            'cep': self.cleaned_data['cep'],
            'complemento': self.cleaned_data['complemento'],
        }

        if self.instance and self.instance.pk and self.instance.endereco:
            # Atualiza o endereço existente
            Endereco.objects.filter(pk=self.instance.endereco.pk).update(**endereco_data)
            endereco = self.instance.endereco
        else:
            # Cria um novo endereço
            endereco = Endereco.objects.create(**endereco_data)

        estagiario = super().save(commit=False)
        estagiario.endereco = endereco

        if self.coordenador:
            estagiario.instituicao = self.coordenador.instituicao

        if commit:
            estagiario.save()

        return estagiario



class EmpresaCadastroForm(forms.ModelForm):
    # Campos para os dados do usuário
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "exemplo@dominio.com"}
        )
    )

    # Campos para os dados de endereço da empresa
    rua = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Rua das Flores'}))
    numero = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número (ex: 123)'}))
    bairro = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bairro (ex: Centro)'}))
    cidade = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cidade (ex: Parnaíba)'}))
    estado = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Estado (ex: PI)'}))
    cep = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CEP (ex: 12345-678)'}))

    # Campos para dados da empresa
    empresa_nome = forms.CharField(max_length=250, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da Empresa (ex: Empresa XYZ)'}))
    empresa_cnpj = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CNPJ (ex: 12.345.678/0001-90)'}))
    empresa_razao_social = forms.CharField(max_length=250, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Razão Social (ex: XYZ Ltda)'}))
    empresa_atividades = forms.CharField(max_length=500, widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Atividade', "rows": 4, "cols": 50}))

    def clean_cpf(self):
        cpf = self.cleaned_data["cpf"]
        cpf = ''.join(filter(str.isdigit, cpf))
        if not validate_cpf(cpf):
            print("CPF inválido")
            raise forms.ValidationError("CPF inválido")
        return cpf

    class Meta: 
        model = Supervisor
        fields = ["primeiro_nome", "sobrenome", "cpf", "cargo", "telefone"]
        widgets = {
            "primeiro_nome": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Primeiro Nome (ex: João)",
                }
            ),
            "sobrenome": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Sobrenome (ex: Silva)"}
            ),
            "cpf": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "CPF (ex: 12345678900)"}
            ),
            "cargo": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Cargo (ex: Gerente de RH)",
                }
            ),
            "telefone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Telefone (ex: 11 91234-5678)",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        self.coordenador = kwargs.pop("coordenador", None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        endereco = Endereco.objects.create(
            rua=self.cleaned_data['rua'],
            numero=self.cleaned_data['numero'],
            bairro=self.cleaned_data['bairro'],
            cidade=self.cleaned_data['cidade'],
            estado=self.cleaned_data['estado'],
            cep=self.cleaned_data['cep']
        )
        
        if self.coordenador:
            empresa = Empresa.objects.create(
                empresa_nome=self.cleaned_data["empresa_nome"],
                cnpj=self.cleaned_data["empresa_cnpj"],
                razao_social=self.cleaned_data["empresa_razao_social"],
                endereco=endereco,
                email=self.cleaned_data["email"],
                instituicao=self.coordenador.instituicao,
            )

    # Atualizando os dados do supervisor
        supervisor.empresa = empresa
        supervisor.email = self.cleaned_data['email']

        if commit:
            supervisor.save()

        return supervisor
    

class ImportEmpresaPDFForm(forms.Form):
    file = forms.FileField(
        widget=forms.FileInput(attrs={"class": "form-control", "accept": ".pdf"})
    )


class CoordenadorEditForm(forms.ModelForm):
    # Campos para os dados do usuário
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control"}))
    primeiro_nome = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    sobrenome = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    cpf = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))

    # Campos para os dados da instituição
    instituicao_nome = forms.CharField(
        max_length=250,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=False,
    )
    instituicao_telefone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=False,
    )

    class Meta:
        model = CoordenadorExtensao
        fields = ["primeiro_nome", "sobrenome", "cpf", "email"]

    def clean_cpf(self):
        cpf = self.cleaned_data["cpf"]
        cpf = ''.join(filter(str.isdigit, cpf))
        if not validate_cpf(cpf):
            print("CPF inválido")
            raise forms.ValidationError("CPF inválido")
        return cpf

    def __init__(self, *args, **kwargs):
        coordenador = kwargs.pop("coordenador")
        super().__init__(*args, **kwargs)
        self.fields["instituicao_nome"].initial = coordenador.instituicao.nome
        self.fields["instituicao_telefone"].initial = coordenador.instituicao.telefone

    def save(self, commit=True):
        user_data = {
            "username": self.cleaned_data["primeiro_nome"]
            + " "
            + self.cleaned_data["sobrenome"],
            "email": self.cleaned_data["email"],
        }

        # Atualiza os dados do usuário
        user = User.objects.filter(username=user_data["username"]).first()

        if user:
            user.username = user_data["username"]
            user.email = user_data["email"]
            user.save()

        coordenador = super().save(commit=False)

        # Atualiza os dados da instituição
        coordenador.instituicao.nome = self.cleaned_data["instituicao_nome"]
        coordenador.instituicao.telefone = self.cleaned_data["instituicao_telefone"]
        coordenador.instituicao.save()

        if commit:
            coordenador.save()

        return coordenador, user
