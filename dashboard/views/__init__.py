from .home import home
from .estagios import add_estagios, detalhes_estagio, complementar_estagio
from .empresa import cadastrar_empresa
from .estagiarios import cadastrar_estagiario
from .pdfimport import importar_pdf
from home.utils import parse_sections
from home.utils import buscar_cep, validate_cnpj
from .instituicao.cadastro_intituicao import cadastrar_instituicao
from .aluno import cadastro_aluno, estagios_aluno, detalhes_estagio_aluno