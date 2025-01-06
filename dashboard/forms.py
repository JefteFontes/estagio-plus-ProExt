from django import forms
from django.contrib.auth.models import User
from .models import Estagiario, Endereco


class EstagiarioCadastroForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'exemplo@dominio.com'}))

    rua = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Rua das Flores'}))
    numero = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número (ex: 123)'}))
    bairro = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bairro (ex: Centro)'}))
    cidade = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cidade (ex: São Paulo)'}))
    estado = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Estado (ex: SP)'}))
    cep = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CEP (ex: 12345-678)'}))

    class Meta:
        model = Estagiario
        fields = ['primeiro_nome', 'sobrenome', 'cpf', 'matricula', 'telefone', 'curso', 'status']
        widgets = {
            'primeiro_nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Primeiro Nome (ex: João)'}),
            'sobrenome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sobrenome (ex: Silva)'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CPF (ex: 12345678900)'}),
            'matricula': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Matrícula (ex: 202312345)'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telefone (ex: 11 91234-5678)'}),
            'curso': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Curso (ex: Engenharia)'}),
            'status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def save(self, commit=True, coordenador=None):
        user_data = {
            'username': self.cleaned_data['primeiro_nome'] + " " + self.cleaned_data['sobrenome'],
            'email': self.cleaned_data['email'],
        }
        password = f"{self.cleaned_data['cpf']}"

        user = User.objects.create_user(**user_data, password=password)

        endereco = Endereco.objects.create(
            rua=self.cleaned_data['rua'],
            numero=self.cleaned_data['numero'],
            bairro=self.cleaned_data['bairro'],
            cidade=self.cleaned_data['cidade'],
            estado=self.cleaned_data['estado'],
            cep=self.cleaned_data['cep']
        )

        # Cria o estagiário
        estagiario = super().save(commit=False)
        estagiario.user = user
        estagiario.endereco = endereco

        # Associa a instituição do coordenador logado
        if coordenador:
            estagiario.instituicao = coordenador.instituicao

        if commit:
            estagiario.save()
            user.save()

        return user, estagiario
