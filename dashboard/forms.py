from django import forms
from django.contrib.auth.models import User
from .views.utils import validate_cpf
from django.core.exceptions import ValidationError
from django.db.models import Min
from dateutil.relativedelta import relativedelta
from .models import (
    Estagiario,
    Endereco,
    Estagio,
    Supervisor,
    Empresa,
    Instituicao,
    TipoChoices,
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
                attrs={"rows": 4, "class": "form-control", "placeholder": "Descrição"}
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
        self.coordenador_extensao = kwargs.pop("coordenador_extensao", None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        cursos = super().save(commit=False)
       
        if self.coordenador_extensao:
            cursos.instituicao = self.coordenador_extensao.instituicao

        if commit:
            cursos.save()
        return cursos


class EstagioCadastroForm(forms.ModelForm):
    bolsa_estagio = forms.FloatField(
        required=False, 
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Bolsa de Estágio (Ex: 500,00)"}
        )
    )
    auxilio_transporte = forms.FloatField(
        required=False, 
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Auxílio Transporte (Ex: 150,00)"}
        )
    )
    area = forms.ChoiceField(
        choices=Areachoices.choices,
        widget=forms.Select(attrs={"class": "form-select"})
    )
    status = forms.ChoiceField(
        choices=StatusChoices.choices,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    descricao = forms.CharField(
        max_length=1000, 
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "placeholder": "Descreva as atividades a serem desenvolvidas no estágio...",
                "rows": 4
            }
        ),
    )
    data_inicio = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "class": "form-control",
                "type": "date", 
                "placeholder": "Data de Início",
            },
            format="%Y-%m-%d", 
        ),
        input_formats=["%Y-%m-%d", "%d/%m/%Y"],
    )
    data_fim = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "class": "form-control",
                "type": "date",
                "placeholder": "Data de Término",
            },
            format="%Y-%m-%d",
        ),
        input_formats=["%Y-%m-%d", "%d/%m/%Y"],
    )
    turno = forms.ChoiceField(
        choices=TurnoChoices.choices,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    estagiario = forms.ModelChoiceField(
        queryset=Estagiario.objects.all(),
        widget=forms.Select(attrs={"class": "form-select"}),
        empty_label="--- Selecione o Estagiário ---"
    )
    empresa = forms.ModelChoiceField(
        queryset=Empresa.objects.all(),
        widget=forms.Select(attrs={"class": "form-select", "id": "empresa-select"}),
        empty_label="--- Selecione a Empresa ---"
    )
    supervisor = forms.ModelChoiceField(
        queryset=Supervisor.objects.all(),
        required=False,
        widget=forms.Select(attrs={"class": "form-select", "id": "supervisor-select"}),
        empty_label="--- Selecione o Supervisor (Opcional) ---"
    )
    instituicao = forms.ModelChoiceField(
        queryset=Instituicao.objects.all(), 
        widget=forms.Select(attrs={"class": "form-select"}),
        empty_label=None
    )
    orientador = forms.CharField(
        max_length=100, 
        required=False, 
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Orientador na Instituição de Ensino (Opcional)"}
        ),
    )
    tipo_estagio = forms.ChoiceField(
        choices=TipoChoices.choices,
        widget=forms.Select(attrs={"class": "form-select"})
    )

    class Meta:
        model = Estagio
        fields = [
            "bolsa_estagio", "auxilio_transporte", "area", "status", "descricao",
            "data_inicio", "data_fim", "turno", "estagiario", "empresa",
            "supervisor", "instituicao", "orientador", "tipo_estagio",
        ]

    def __init__(self, *args, **kwargs):
        current_user = kwargs.pop("user", None)
        kwargs.pop("empresa_id", None)
        kwargs.pop("instituicao_id", None)
        super().__init__(*args, **kwargs)

        instituicao_logada = None
        if current_user and current_user.is_authenticated:
            coordenador_extensao = CoordenadorExtensao.objects.filter(user=current_user).first()
            if coordenador_extensao and coordenador_extensao.instituicao:
                instituicao_logada = coordenador_extensao.instituicao

        if instituicao_logada:
            self.fields["estagiario"].queryset = Estagiario.objects.filter(instituicao=instituicao_logada).order_by('nome_completo')
            self.fields["empresa"].queryset = Empresa.objects.filter(instituicao=instituicao_logada).order_by('empresa_nome')

            self.fields["instituicao"].queryset = Instituicao.objects.filter(id=instituicao_logada.id)
            self.fields["instituicao"].initial = instituicao_logada
            self.fields["instituicao"].disabled = True 
            self.fields["supervisor"].queryset = Supervisor.objects.filter(empresa__instituicao=instituicao_logada).order_by('nome_completo')
        else:
            self.fields["estagiario"].queryset = Estagiario.objects.none()
            self.fields["empresa"].queryset = Empresa.objects.none()
            self.fields["instituicao"].queryset = Instituicao.objects.none()
            self.fields["supervisor"].queryset = Supervisor.objects.none()

    def clean(self):
        cleaned_data = super().clean()

        estagiario_selecionado = cleaned_data.get("estagiario")
        empresa_selecionada = cleaned_data.get("empresa")
        turno_estagio_proposto = cleaned_data.get("turno")
        data_inicio_proposta = cleaned_data.get("data_inicio")
        data_fim_proposta = cleaned_data.get("data_fim")
        status_proposto = cleaned_data.get("status")

        if not all([estagiario_selecionado, empresa_selecionada, turno_estagio_proposto,
                    data_inicio_proposta, data_fim_proposta, status_proposto]):
            return cleaned_data

        # 1. Turno do estagiário e turno do estágio proposto devem ser diferentes
        if estagiario_selecionado.turno == turno_estagio_proposto:
            self.add_error("turno", "O turno do estágio não pode ser o mesmo do curso regular do estagiário.")

        # 2. Data de inicio do estágio proposto deve ser posterior a data de inicio do estagiário
        if data_inicio_proposta < estagiario_selecionado.data_inicio:
            self.add_error("data_inicio", "A data de início do estágio deve ser posterior ou igual a data de início do estudante.")

        # 3. Data de fim do estágio proposto deve ser posterior a data de inicio do estágio
        if data_fim_proposta < data_inicio_proposta:
            self.add_error("data_fim", "A data de término do estágio deve ser posterior à data de início.")

        # 3. Período mínimo do estagiário para iniciar um estágio
        if estagiario_selecionado.periodo < 4: # Exemplo: Mínimo 3 períodos concluídos (estar no 4º)
            self.add_error("estagiario", "O estudante precisa ter concluído no mínimo 03 (três) períodos letivos do curso para iniciar um estágio.")

        # 4. Conflito de turno/data com outro estágio ATIVO do mesmo estagiário
        #    Um estagiário não pode ter dois estágios "Em andamento" no mesmo turno com datas sobrepostas.
        query_conflito_turno = Estagio.objects.filter(
            estagiario=estagiario_selecionado,
            turno=turno_estagio_proposto,
            status=StatusChoices.em_andamento
        ).exclude( 
            data_fim__lt=data_inicio_proposta  
        ).exclude(
            data_inicio__gt=data_fim_proposta  
        )

        if self.instance and self.instance.pk: 
            query_conflito_turno = query_conflito_turno.exclude(pk=self.instance.pk)
            
        if query_conflito_turno.exists():
            estagio_conflitante = query_conflito_turno.first()
            nome_empresa_conflitante = estagio_conflitante.empresa.empresa_nome if estagio_conflitante.empresa else "Empresa não informada"
            self.add_error(None, ValidationError(
                f"Este estagiário já possui um estágio 'Em andamento' (Empresa: {nome_empresa_conflitante}, "
                f"Período: {estagio_conflitante.data_inicio.strftime('%d/%m/%Y')} - {estagio_conflitante.data_fim.strftime('%d/%m/%Y')}) "
                f"que conflita com o turno e as datas propostas.", code="conflito_estagio_ativo"
            ))

        # 5. Limite cumulativo de 2 anos de estágio na mesma empresa
        db_earliest_start_agg = Estagio.objects.filter(
            estagiario=estagiario_selecionado,
            empresa=empresa_selecionada
        ).aggregate(min_db_start=Min('data_inicio'))
        
        earliest_start_from_db = db_earliest_start_agg.get('min_db_start')

        if earliest_start_from_db:
            primeira_data_inicio_geral_na_empresa = min(earliest_start_from_db, data_inicio_proposta)
        else:
            primeira_data_inicio_geral_na_empresa = data_inicio_proposta
            
        data_limite_cumulativa = primeira_data_inicio_geral_na_empresa + relativedelta(years=2)

        if data_fim_proposta > data_limite_cumulativa:
            self.add_error(
                "data_fim", 
                ValidationError(
                    f"A data de término ({data_fim_proposta.strftime('%d/%m/%Y')}) excede o limite total de 2 anos "
                    f"de estágio para {estagiario_selecionado.nome_completo} na empresa {empresa_selecionada.empresa_nome}. "
                    f"O período de estágio nesta empresa iniciou-se em {primeira_data_inicio_geral_na_empresa.strftime('%d/%m/%Y')}, "
                    f"portanto, o estágio deve ser concluído até {data_limite_cumulativa.strftime('%d/%m/%Y')}.",
                    code="limite_cumulativo_2_anos"
                )
            )

        # 6. Validações específicas para edição de um estágio existente (prorrogação/alteração)
        if self.instance and self.instance.pk:
            try:
                estagio_original_db = Estagio.objects.get(pk=self.instance.pk)
                if data_inicio_proposta < estagio_original_db.data_inicio:
                    self.add_error("data_inicio",
                                   f"Ao alterar este estágio, a nova data de início ({data_inicio_proposta.strftime('%d/%m/%Y')}) "
                                   f"não pode ser anterior à data de início original deste contrato ({estagio_original_db.data_inicio.strftime('%d/%m/%Y')}).")
            except Estagio.DoesNotExist:
               
                pass 

        if not self.errors:
            try:
                temp_estagio_instance = Estagio(
                    pk=self.instance.pk if self.instance and self.instance.pk else None,
                    bolsa_estagio=cleaned_data.get("bolsa_estagio", 0.0), 
                    auxilio_transporte=cleaned_data.get("auxilio_transporte", 0.0),
                    area=cleaned_data.get("area"), 
                    status=status_proposto,
                    descricao=cleaned_data.get("descricao"),
                    data_inicio=data_inicio_proposta,
                    data_fim=data_fim_proposta,
                    turno=turno_estagio_proposto,
                    estagiario=estagiario_selecionado,
                    empresa=empresa_selecionada,
                    supervisor=cleaned_data.get("supervisor"),
                    instituicao=cleaned_data.get("instituicao"), 
                    orientador=cleaned_data.get("orientador"),
                    tipo_estagio=cleaned_data.get("tipo_estagio")
                )
                temp_estagio_instance.clean()
            except ValidationError as e:
                if hasattr(e, 'message_dict'): 
                    for field, messages in e.message_dict.items():
                        self.add_error(field if field != '__all__' else None, messages)
                elif hasattr(e, 'messages'):
                     for message in e.messages:
                        self.add_error(None, message)
                else:
                    self.add_error(None, str(e))
            except Exception as e:
                self.add_error(None, f"Ocorreu um erro inesperado na validação dos dados: {str(e)}. Por favor, contate o suporte.")

        return cleaned_data

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

    def clean_cpf(self):
        cpf = self.cleaned_data["cpf"]
        cpf = "".join(filter(str.isdigit, cpf))
        if not validate_cpf(cpf):
            raise forms.ValidationError("CPF inválido")
        return cpf

    class Meta:
        model = Estagiario
        fields = [
            "nome_completo",
            "cpf",
            "matricula",
            "telefone",
            "curso",
            "status",
            "email",
            "periodo",
            "turno",
        ]
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
            "matricula": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Matrícula (ex: 202312345)",
                }
            ),
            "turno": forms.Select(attrs={"class": "form-control"}),
            "periodo": forms.NumberInput(attrs={"class": "form-control","placeholder": "Período (ex:1)","min":"1","max":"8" }),
            "telefone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Telefone (ex: 86 91234-5678)",
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
        self.instituicao = kwargs.pop("instituicao", None)
        super().__init__(*args, **kwargs)

        # Preenche os campos de endereço, caso o estagiário já tenha um endereço associado
        if self.instance and self.instance.pk and self.instance.endereco:
            endereco = self.instance.endereco
            self.fields["rua"].initial = endereco.rua
            self.fields["numero"].initial = endereco.numero
            self.fields["bairro"].initial = endereco.bairro
            self.fields["cidade"].initial = endereco.cidade
            self.fields["estado"].initial = endereco.estado
            self.fields["cep"].initial = endereco.cep
            self.fields["complemento"].initial = endereco.complemento

        # Use coordenador.instituicao or fallback to self.instituicao
        instituicao = None
        if self.coordenador and self.coordenador.instituicao:
            instituicao = self.coordenador.instituicao
        elif self.instituicao:
            instituicao = self.instituicao

        if instituicao:
            self.fields["curso"].queryset = Cursos.objects.filter(
                instituicao=instituicao
            )
        else:
            self.fields["curso"].queryset = Cursos.objects.none()

    def save(self, commit=True):
        # Salva ou atualiza o endereço
        endereco_data = {
            "rua": self.cleaned_data["rua"],
            "numero": self.cleaned_data["numero"],
            "bairro": self.cleaned_data["bairro"],
            "cidade": self.cleaned_data["cidade"],
            "estado": self.cleaned_data["estado"],
            "cep": self.cleaned_data["cep"],
            "complemento": self.cleaned_data["complemento"],
        }

        if self.instance and self.instance.pk and self.instance.endereco:
            # Atualiza o endereço existente
            Endereco.objects.filter(pk=self.instance.endereco.pk).update(
                **endereco_data
            )
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
    # Campos para dados da empresa
    empresa_nome = forms.CharField(
        max_length=250,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Nome da Empresa (ex: Empresa XYZ)",
            }
        ),
    )
    empresa_cnpj = forms.CharField(
        max_length=20,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "CNPJ (ex: 12.345.678/0001-90)",
            }
        ),
    )
    empresa_razao_social = forms.CharField(
        max_length=250,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Razão Social (ex: XYZ Ltda)",
            }
        ),
    )
    empresa_atividades = forms.CharField(
        max_length=500,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "placeholder": "Atividade",
                "rows": 4,
                "cols": 50,
            }
        ),
    )

    def clean_cpf(self):
        cpf = self.cleaned_data["cpf"]
        cpf = "".join(filter(str.isdigit, cpf))
        if not validate_cpf(cpf):
            print("CPF inválido")
            raise forms.ValidationError("CPF inválido")
        return cpf

    class Meta:
        model = Supervisor
        fields = ["nome_completo", "cpf", "cargo", "telefone"]
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
        if self.instance.pk:
            supervisor = self.instance
            empresa = supervisor.empresa
            endereco = empresa.endereco
        else:
            supervisor = super().save(commit=False)
            endereco = Endereco()
            empresa = Empresa()

        # Atualizando os dados do endereço
        endereco.rua = self.cleaned_data["rua"]
        endereco.numero = self.cleaned_data["numero"]
        endereco.bairro = self.cleaned_data["bairro"]
        endereco.cidade = self.cleaned_data["cidade"]
        endereco.estado = self.cleaned_data["estado"]
        endereco.cep = self.cleaned_data["cep"]
        endereco.complemento = self.cleaned_data["complemento"]
        endereco.save()

        # Atualizando os dados da empresa
        empresa.empresa_nome = self.cleaned_data["empresa_nome"]
        empresa.cnpj = self.cleaned_data["empresa_cnpj"]
        empresa.razao_social = self.cleaned_data["empresa_razao_social"]
        empresa.endereco = endereco
        empresa.email = self.cleaned_data["email"]

        if not self.instance.pk:  # Só cria uma nova empresa se não for edição
            empresa = Empresa.objects.create(
                empresa_nome=self.cleaned_data["empresa_nome"],
                cnpj=self.cleaned_data["empresa_cnpj"],
                razao_social=self.cleaned_data["empresa_razao_social"],
                endereco=endereco,
                email=self.cleaned_data["email"],
                instituicao=self.coordenador.instituicao,
            )
        else:
            empresa.save()  # Apenas salva se for uma edição

        # Atualizando os dados do supervisor
        supervisor.empresa = empresa
        supervisor.email = self.cleaned_data["email"]

        if commit:
            supervisor.save()

        return supervisor


class CoordenadorEditForm(forms.ModelForm):
    # Fields for user data
    email = forms.EmailField(
        label="E-mail", widget=forms.EmailInput(attrs={"class": "form-control"})
    )
    nome_completo = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    cpf = forms.CharField(
        label="CPF", widget=forms.TextInput(attrs={"class": "form-control"})
    )
    # Fields for institution data
    instituicao_nome = forms.CharField(
        label="Nome da instituição",
        max_length=250,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=False,
    )
    instituicao_telefone = forms.CharField(
        label="Telefone da instituição",
        max_length=20,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=False,
    )
    instituicao_logo = forms.ImageField(
        label="Logo da instituição",
        widget=forms.ClearableFileInput(attrs={"class": "form-control"}),
        required=False,
    )

    class Meta:
        model = CoordenadorExtensao
        fields = ["nome_completo", "cpf", "email"]

    def __init__(self, *args, **kwargs):
        # Extract the 'coordenador' argument if provided
        coordenador = kwargs.pop("coordenador", None)
        super().__init__(*args, **kwargs)
        # Prepopulate institution fields if 'coordenador' is provided
        if coordenador and coordenador.instituicao:
            self.fields["instituicao_nome"].initial = coordenador.instituicao.nome
            self.fields["instituicao_telefone"].initial = (
                coordenador.instituicao.telefone
            )
            self.fields["instituicao_logo"].initial = coordenador.instituicao.logo

    def save(self, commit=True):
        # Update the related User model
        coordenador = super().save(commit=False)
        user = coordenador.user  # Access the related User model
        # Update user fields
        user.username = f"{self.cleaned_data['nome_completo']}"
        user.email = self.cleaned_data["email"]
        user.save()
        # Update institution fields
        if coordenador.instituicao:
            coordenador.instituicao.nome = self.cleaned_data["instituicao_nome"]
            coordenador.instituicao.telefone = self.cleaned_data["instituicao_telefone"]

            new_logo = self.cleaned_data.get("instituicao_logo")
            if new_logo:
                coordenador.instituicao.logo = new_logo

            coordenador.instituicao.save()
        if commit:
            coordenador.save()
        return coordenador
