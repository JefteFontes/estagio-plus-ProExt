import datetime
import os
from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST

from home.utils import preencher_tceu
from mais_estagio.forms import AlunoCadastroEstagioForm
from ..forms import EstagioCadastroForm
from ..models import Empresa, Estagio, Supervisor, RelatorioEstagio
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def formatar_duracao(diferenca):
    partes = [
        f"{diferenca.years} ano(s)" if diferenca.years else "",
        f"{diferenca.months} mes(es)" if diferenca.months else "",
        (
            f"{diferenca.days} dia(s)"
            if diferenca.days or not (diferenca.years or diferenca.months)
            else ""
        ),
    ]
    return ", ".join([p for p in partes if p])


def estagio_duracao(estagio):
    diferenca = relativedelta(estagio.data_fim, estagio.data_inicio)
    return formatar_duracao(diferenca)


def estagio_falta_dias(estagio):
    hoje = datetime.date.today()
    if estagio.data_fim < hoje:
        return "0 dias"  # Estágio já finalizado
    diferenca = relativedelta(estagio.data_fim, hoje)
    return formatar_duracao(diferenca)


def verificar_relatorios_pendentes(estagio):
    hoje = datetime.date.today()
    relatorios = []

    # Termo de compromisso
    if hoje >= estagio.data_inicio and not estagio.pdf_termo:
        relatorios.append(
            {"tipo": "Termo de Compromisso", "data_prevista": estagio.data_inicio}
        )

    data = estagio.data_inicio + relativedelta(months=6)
    while data <= hoje and data < estagio.data_fim:
        relatorios.append({"tipo": "Relatório Semestral", "data_prevista": data})
        data += relativedelta(months=6)

    if hoje >= estagio.data_fim:
        for tipo in ["Relatório de Avaliação", "Relatório de Conclusão"]:
            relatorios.append({"tipo": tipo, "data_prevista": estagio.data_fim})

    return relatorios


def verificar_relatorios_atrasados(request):
    hoje = datetime.date.today()
    relatorios_por_estagiario = {}  

    coordenador = request.user.coordenadorextensao
    instituicao = coordenador.instituicao
    estagios = Estagio.objects.filter(instituicao=instituicao)

    for estagio in estagios:
        relatorios_pendentes = verificar_relatorios_pendentes(estagio)
        relatorios_proximos_vencimento = []

        for relatorio in relatorios_pendentes:
            data_prevista = relatorio['data_prevista']
            dias_para_vencer = (data_prevista - hoje).days

            if dias_para_vencer <= 30: 
                relatorios_proximos_vencimento.append({
                    'tipo': relatorio['tipo'],
                    'data_prevista': data_prevista
                })

        if relatorios_proximos_vencimento:
            relatorios_por_estagiario[estagio] = relatorios_proximos_vencimento

    if not relatorios_por_estagiario:
        return False

    # CORREÇÃO: Verifique se hoje não é None (não é necessário, mas mantenha o padrão)
    hoje_str = hoje.strftime("%d/%m/%Y") if hoje else ""

    context = {
        'user_name': request.user.get_full_name() or request.user.username,
        'relatorios_por_estagiario': relatorios_por_estagiario,
        'site_name': settings.SITE_NAME,
        'site_url': request.build_absolute_uri('/'),
        'hoje': hoje_str,
    }

    email_content = render_to_string("emails/relatorio_notificacao_coordenador.txt", context)

    send_mail(
        subject=_('Relatórios de estágio pendentes - {}').format(hoje_str),
        message=email_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[request.user.email],
        fail_silently=False,
    )

    return True


def notificar_estagiarios_relatorios_pendentes(request):
    hoje = datetime.date.today()
    estagios_com_pendencias = []

    coordenador = request.user.coordenadorextensao
    instituicao = coordenador.instituicao
    estagios = Estagio.objects.filter(instituicao=instituicao)

    for estagio in estagios:
        relatorios_pendentes = verificar_relatorios_pendentes(estagio)
        relatorios_proximos_vencimento = []

        for relatorio in relatorios_pendentes:
            data_prevista = relatorio['data_prevista']
            dias_para_vencer = (data_prevista - hoje).days

            if dias_para_vencer <= 30:  
                relatorios_proximos_vencimento.append({
                    'tipo': relatorio['tipo'],
                    'data_prevista': data_prevista,
                    'dias_atraso': max(0, (hoje - data_prevista).days) if hoje > data_prevista else 0
                })

        if relatorios_proximos_vencimento:
            # CORREÇÃO: Use strftime só se hoje não for None
            hoje_str = hoje.strftime("%d/%m/%Y") if hoje else ""
            curso_nome = estagio.estagiario.curso.nome_curso if estagio.estagiario.curso else ''
            context = {
                'estagiario_nome': estagio.estagiario.nome_completo,
                'relatorios_pendentes': relatorios_proximos_vencimento,
                'site_name': settings.SITE_NAME,
                'site_url': request.build_absolute_uri('/'),
                'hoje': hoje_str,
                'curso': curso_nome,
            }

            email_content = render_to_string("emails/relatorio_notificacao_estagiario.txt", context)

            send_mail(
                subject=f'Relatórios de estágio pendentes - {hoje_str}',
                message=email_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[estagio.estagiario.email],
                fail_silently=False,
            )

            estagios_com_pendencias.append(estagio)

    return len(estagios_com_pendencias) > 0


def processar_form_estagio(request, estagio=None):
    template_to_render = "add_estagios.html"
    form_class = EstagioCadastroForm 
    form_kwargs = {'instance': estagio, 'user': request.user} 

    if hasattr(request.user, "aluno") and request.user.aluno:
        template_to_render = "aluno/cadastrar_estagio.html"
        form_class = AlunoCadastroEstagioForm 
        form_kwargs = {'instance': estagio, 'user': request.user, 'aluno_logado': request.user.aluno} 

    if request.method == "POST":
        form = form_class(request.POST, **form_kwargs) 
        if form.is_valid():
            estagio_instance = form.save()

            template_path = str(os.path.join(settings.BASE_DIR, "mais_estagio", "templates", "docs", "TceuTemplate.docx"))

            output_pdf_path = preencher_tceu(estagio_instance, template_path)

            if output_pdf_path and os.path.exists(str(output_pdf_path)): 

                relative_path = str(output_pdf_path).replace(str(settings.MEDIA_ROOT), '').lstrip('/')
                estagio_instance.pdf_termo.name = relative_path
                estagio_instance.save()

                with open(str(output_pdf_path), 'rb') as fh: 
                    response = HttpResponse(fh.read(), content_type="application/pdf")
                    filename = os.path.basename(str(output_pdf_path)) 
                    response['Content-Disposition'] = f'attachment; filename="{filename}"'

                    messages.success(request, "Estágio salvo com sucesso!")
                    if hasattr(request.user, "aluno") and request.user.aluno:
                        return redirect('estagio_andamento')
                    else:
                        return redirect('dashboard_instituicao')
            else:
                messages.error(request, "O documento PDF não pôde ser gerado.")
                raise Http404("O documento PDF não pôde ser gerado.")
        else:
            messages.error(request, "Erro ao salvar estágio.")
    else:
        form = form_class(**form_kwargs) 

    return render(request, template_to_render, {"form": form, "estagio": estagio})


@login_required
@user_passes_test(lambda u: hasattr(u, "coordenadorextensao") and u.coordenadorextensao)
def add_estagios(request):
    return processar_form_estagio(request)


@login_required
@user_passes_test(lambda u: hasattr(u, "coordenadorextensao") and u.coordenadorextensao)
def editar_estagio(request, estagio_id):
    estagio = get_object_or_404(Estagio, id=estagio_id)
    return processar_form_estagio(request, estagio)


@login_required
def complementar_estagio(request, estagio_id):
    estagio = get_object_or_404(Estagio, id=estagio_id)
    return processar_form_estagio(
        request, estagio, template="complementar_estagio.html"
    )


@login_required
def verificar_pendencias(request):
    notificou_coordenador = verificar_relatorios_atrasados(request)
    notificou_estagiarios = notificar_estagiarios_relatorios_pendentes(request)
    
    if notificou_coordenador or notificou_estagiarios:
        messages.success(request, "Notificações enviadas com sucesso!")
    else:
        messages.info(request, "Nenhum relatório pendente encontrado.")
    
    return redirect('dashboard_instituicao')


@login_required
def detalhes_estagio(request):
    selected = request.GET.get("selected")
    if not selected:
        return JsonResponse({"error": 'Parâmetro "selected" ausente.'}, status=400)

    estagio = get_object_or_404(Estagio, id=selected)
    duracao = estagio_duracao(estagio)
    tempo_falta = estagio_falta_dias(estagio)
    relatorios_pendentes = verificar_relatorios_pendentes(estagio)
    documento_path = None
    documento_url = None
    if estagio.pdf_termo:
        documento_path = os.path.join(settings.MEDIA_ROOT, estagio.pdf_termo.name)
        documento_url = estagio.pdf_termo.url if hasattr(estagio.pdf_termo, 'url') else None

    # Escolha do template base conforme o tipo de usuário
    if hasattr(request.user, "coordenadorextensao") and request.user.coordenadorextensao:
        template = "details.html"  # Usa base institucional
    elif hasattr(request.user, "orientador") and request.user.orientador:
        template = "orientador/detalhes_estagio_orientador.html"
    elif hasattr(request.user, "supervisor") and request.user.supervisor:
        template = "supervisor/detalhes_estagio_supervisor.html"
    elif hasattr(request.user, "aluno") and request.user.aluno:
        template = "aluno/detalhes_estagio_aluno.html"
    else:
        # fallback seguro
        template = "details.html"

    return render(
        request,
        template,
        {
            "estagio": estagio,
            "duracao": duracao,
            "tempo_falta": tempo_falta,
            "relatorios_pendentes": relatorios_pendentes,
            "documento_path": documento_path,
            "documento_url": documento_url,
            "documento_existe": os.path.exists(documento_url) if documento_url else False,
        },
    )


@login_required
def get_supervisores(request):
    empresa_id = request.GET.get("empresa_id")
    if empresa_id:
        supervisores = Supervisor.objects.filter(empresa_id=empresa_id).order_by("nome_completo")
        print("DEBUG supervisores:", list(supervisores))
        data = [{"id": s.id, "nome_completo": s.nome_completo} for s in supervisores]
        return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False)


def download_tceu(request, estagio_id):
    estagio = get_object_or_404(Estagio, id=estagio_id)

    if not estagio.pdf_termo:
        raise Http404("Documento não encontrado.")
    
    file_path = os.path.join(settings.MEDIA_ROOT, estagio.pdf_termo.name)
    
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/pdf")
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
            return response
    else:
        raise Http404("Documento não encontrado.")


def importar_termo(request, estagio_id):
    estagio = get_object_or_404(Estagio, pk=estagio_id)
    
    if request.method == 'POST':
        # Verifica se o arquivo foi enviado
        print("Request Files:", request.FILES)
        print("Request POST:", request.POST)

        if 'pdf_termo' not in request.FILES:  # Alterado para 'documento' que é o name do input
            return JsonResponse({'status': 'error', 'message': 'Nenhum arquivo enviado'}, status=400)

        arquivo = request.FILES['pdf_termo']

        # Validações do arquivo
        if arquivo.size > settings.MAX_UPLOAD_SIZE:
            return JsonResponse({
                'status': 'error',
                'message': f'Arquivo muito grande (máximo {settings.MAX_UPLOAD_SIZE/1024/1024}MB)'
            }, status=400)

        if not arquivo.name.lower().endswith('.pdf'):
            return JsonResponse({'status': 'error', 'message': 'Apenas arquivos PDF são permitidos'}, status=400)

        try:
            # Remove o arquivo antigo se existir
            if estagio.pdf_termo:
                estagio.pdf_termo = None
                estagio.save() # Usando delete() que é mais seguro

            # Salva o novo arquivo
            estagio.pdf_termo.save(arquivo.name, arquivo)

            return JsonResponse({
                'status': 'success',
                'message': 'Documento importado com sucesso',
                'file_url': estagio.pdf_termo.url
            })

        except Exception as e:
            logger.error(f"Erro ao importar documento: {str(e)}", exc_info=True)
            return JsonResponse({
                'status': 'error',
                'message': 'Erro interno ao processar o documento'
            }, status=500)

    return JsonResponse({'status': 'error', 'message': 'Método não permitido'}, status=405)