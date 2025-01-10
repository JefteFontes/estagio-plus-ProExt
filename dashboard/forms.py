from django import forms
from django.contrib.auth.models import User
from .models import Estagiario, Endereco, Estagio, Supervisor, Empresa, Instituicao, TurnoChoices


##############################################
############ CADASTRO ESTÁGIO ################
##############################################
class EstagioCadastroForm(forms.ModelForm):
    bolsa_estagio = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Bolsa de Estágio'}))
    area = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Área'}))
    status = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))  
    descricao = forms.CharField(max_length=255, widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descrição',"rows": 4, "cols": 50}))
    auxilio_transporte = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Auxilio de Transporte'}))
    data_inicio = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'placeholder': 'Data de Início'}))
    data_fim = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'placeholder': 'Data de Fim'}))
    turno = forms.ChoiceField(choices=TurnoChoices.choices, widget=forms.Select(attrs={'class': 'form-select'}))
    estagiario = forms.ModelChoiceField(queryset=Estagiario.objects.all(), widget=forms.Select(attrs={'class': 'form-select'}))
    empresa = forms.ModelChoiceField(queryset=Empresa.objects.all(), widget=forms.Select(attrs={'class': 'form-select'}),)
    #supervisor somente os da empresa selecionada
    supervisor = forms.ModelChoiceField(queryset=Supervisor.objects.all(), widget=forms.Select(attrs={'class': 'form-select'}))
    instituicao = forms.ModelChoiceField(queryset=Instituicao.objects.all(), widget=forms.Select(attrs={'class': 'form-select'}))
    
    class Meta:
        model = Estagio
        fields = ['bolsa_estagio', 'auxilio_transporte', 'area', 'status', 'descricao', 'data_inicio', 'data_fim', 'turno', 'estagiario', 'empresa', 'supervisor', 'instituicao']
        widgets = {
            'bolsa_estagio': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Bolsa de Estágio'}),
            'auxilio_transporte': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Auxilio de Transporte'}),
            'area': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Área'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descrição'}),
            'turno': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Turno'}),
            'estagiario': forms.Select(attrs={'class': 'form-control'}),
            'empresa': forms.Select(attrs={'class': 'form-control'}),
            'supervisor': forms.Select(attrs={'class': 'form-control'}),
            'instituicao': forms.Select(attrs={'class': 'form-control'})
        }

    def save(self, commit=True):
        estagio = super().save(commit=False)
        if commit:
            estagio.save()
        return estagio
        
###############################################        
######CADASTRO DE ESTAGIARIO - ALUNO ##########
###############################################   
class EstagiarioCadastroForm(forms.ModelForm):
    rua = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Rua das Flores'}))
    numero = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número (ex: 123)'}))
    bairro = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bairro (ex: Centro)'}))
    cidade = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cidade (ex: São Paulo)'}))
    estado = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Estado (ex: SP)'}))
    cep = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CEP (ex: 12345-678)'}))

    class Meta:
        model = Estagiario
        fields = ['primeiro_nome', 'sobrenome', 'cpf', 'matricula', 'telefone', 'curso', 'status', 'email']
        widgets = {
            'primeiro_nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Primeiro Nome (ex: João)'}),
            'sobrenome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sobrenome (ex: Silva)'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CPF (ex: 12345678900)'}),
            'matricula': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Matrícula (ex: 202312345)'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telefone (ex: 11 91234-5678)'}),
            'curso': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Curso (ex: Engenharia)'}),
            'status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'exemplo@dominio.com'})
        }

    def save(self, commit=True):
        endereco = Endereco.objects.create(
            rua=self.cleaned_data['rua'],
            numero=self.cleaned_data['numero'],
            bairro=self.cleaned_data['bairro'],
            cidade=self.cleaned_data['cidade'],
            estado=self.cleaned_data['estado'],
            cep=self.cleaned_data['cep']
        )

        estagiario = super().save(commit=False)
        estagiario.endereco = endereco

        if commit:
            estagiario.save()

        return estagiario

#####################################
########CADASTRO DE EMPRESA##########
#####################################
class EmpresaCadastroForm(forms.ModelForm):
    # Campos para os dados do usuário
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'exemplo@dominio.com'}))

    # Campos para os dados de endereço da empresa
    rua = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Rua das Flores'}))
    numero = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número (ex: 123)'}))
    bairro = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bairro (ex: Centro)'}))
    cidade = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cidade (ex: São Paulo)'}))
    estado = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Estado (ex: SP)'}))
    cep = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CEP (ex: 12345-678)'}))

    # Campos para dados da empresa
    empresa_nome = forms.CharField(max_length=250, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da Empresa (ex: Empresa XYZ)'}))
    empresa_cnpj = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CNPJ (ex: 12.345.678/0001-90)'}))
    empresa_razao_social = forms.CharField(max_length=250, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Razão Social (ex: XYZ Ltda)'}))

    class Meta:
        model = Supervisor
        fields = ['primeiro_nome', 'sobrenome', 'cpf', 'cargo', 'telefone']
        widgets = {
            'primeiro_nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Primeiro Nome (ex: João)'}),
            'sobrenome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sobrenome (ex: Silva)'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CPF (ex: 12345678900)'}),
            'cargo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cargo (ex: Gerente de RH)'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telefone (ex: 11 91234-5678)'}),
        }

    def save(self, commit=True):
        endereco = Endereco.objects.create(
            rua=self.cleaned_data['rua'],
            numero=self.cleaned_data['numero'],
            bairro=self.cleaned_data['bairro'],
            cidade=self.cleaned_data['cidade'],
            estado=self.cleaned_data['estado'],
            cep=self.cleaned_data['cep']
        )

        empresa = Empresa.objects.create(
            nome=self.cleaned_data['empresa_nome'],
            cnpj=self.cleaned_data['empresa_cnpj'],
            razao_social=self.cleaned_data['empresa_razao_social'],
            endereco=endereco,
            email = self.cleaned_data['email'] 
        )

        # Cria o coordenador de extensão
        supervisor = super().save(commit=False)
        supervisor.empresa = empresa
        supervisor.email = self.cleaned_data['email'] 

        if commit:
            supervisor.save()

        return supervisor
    
class ImportEmpresaPDFForm(forms.Form):
    file = forms.FileField(widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf'}))
