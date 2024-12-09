from django import forms
from django.contrib.auth.models import User
from dashboard.models import CoordenadorExtensao, Instituicao, Endereco

class CoordenadorCadastroForm(forms.ModelForm):
    # Campos para os dados do usuário
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'exemplo@dominio.com'}))

    # Campos para os dados do endereço da instituição
    rua = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Rua das Flores'}))
    numero = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número (ex: 123)'}))   
    bairro = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bairro (ex: Centro)'}))
    cidade = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cidade (ex: São Paulo)'}))
    estado = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Estado (ex: SP)'}))
    cep = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CEP (ex: 12345-678)'}))

    # Campos para os dados da instituição
    instituicao_nome = forms.CharField(max_length=250, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da Instituição (ex: Universidade XYZ)'}))
    instituicao_cnpj = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CNPJ (ex: 12.345.678/0001-90)'}))
    instituicao_telefone = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telefone (ex: 11 1234-5678)'})) 

    class Meta:
        model = CoordenadorExtensao
        fields = ['primeiro_nome', 'sobrenome', 'cpf']
        widgets = {
            'primeiro_nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Primeiro Nome (ex: João)'}),
            'sobrenome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sobrenome (ex: Silva)'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CPF (ex: 12345678900)'}),
        }

    def save(self, commit=True):
        # Captura os dados do formulário
        user_data = {
            'username': self.cleaned_data['primeiro_nome'] + " " + self.cleaned_data['sobrenome'],
            'email': self.cleaned_data['email'],
        }
        password = f"{self.cleaned_data['cpf']}"
        
        print(password)   # Gera uma senha com CPF

        # Cria o usuário
        user = User.objects.create_user(**user_data, password=password)

        # Cria o endereço da instituição
        endereco = Endereco.objects.create(
            rua=self.cleaned_data['rua'],
            numero=self.cleaned_data['numero'],
            bairro=self.cleaned_data['bairro'],
            cidade=self.cleaned_data['cidade'],
            estado=self.cleaned_data['estado'],
            cep=self.cleaned_data['cep']
        )

        # Cria a instituição
        instituicao = Instituicao.objects.create(
            nome=self.cleaned_data['instituicao_nome'],
            cnpj=self.cleaned_data['instituicao_cnpj'],
            telefone=self.cleaned_data['instituicao_telefone'],
            email=self.cleaned_data['email'],
            endereco=endereco
        )

        # Cria o coordenador de extensão
        coordenador = super().save(commit=False)
        coordenador.instituicao = instituicao
        coordenador.email = self.cleaned_data['email'] 
        if commit:
            coordenador.save()
            user.save()

        return user, coordenador
