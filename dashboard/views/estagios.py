import datetime
import os
from .utils import preencher_tceu
from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from ..forms import EstagioCadastroForm
from ..models import Empresa, Estagio, Supervisor, RelatorioEstagio
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from django.conf import settings


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
    if hoje >= estagio.data_inicio:
        relatorios.append(
            {"tipo": "Termo de Compromisso", "data_prevista": estagio.data_inicio}
        )

    # Relatórios semestrais
    data = estagio.data_inicio + relativedelta(months=6)
    while data <= hoje and data < estagio.data_fim:
        relatorios.append({"tipo": "Relatório Semestral", "data_prevista": data})
        data += relativedelta(months=6)

    # Relatórios finais
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
    
    context = {
        'user_name': request.user.get_full_name() or request.user.username,
        'relatorios_por_estagiario': relatorios_por_estagiario,
        'site_name': settings.SITE_NAME,
        'site_url': request.build_absolute_uri('/'),
        'hoje': hoje.strftime("%d/%m/%Y"),
    }

    email_content = render_to_string("emails/relatorio_notificacao_coordenador.txt", context)

    send_mail(
        subject=_('Relatórios de estágio pendentes - {}').format(hoje.strftime("%d/%m/%Y")),
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
            context = {
                'estagiario_nome': estagio.estagiario.nome,
                'relatorios_pendentes': relatorios_proximos_vencimento,
                'site_name': settings.SITE_NAME,
                'site_url': request.build_absolute_uri('/'),
                'hoje': hoje.strftime("%d/%m/%Y"),
                'curso': estagio.estagiario.curso.nome_curso if estagio.estagiario.curso else '',
            }

            email_content = render_to_string("emails/relatorio_notificacao_estagiario.txt", context)

            send_mail(
                subject=f'Relatórios de estágio pendentes - {hoje.strftime("%d/%m/%Y")}',
                message=email_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[estagio.estagiario.email],
                fail_silently=False,
            )
            
            estagios_com_pendencias.append(estagio)
    
    return len(estagios_com_pendencias) > 0


def processar_form_estagio(request, estagio=None, template="add_estagios.html"):
    if request.method == "POST":
        form = EstagioCadastroForm(request.POST, instance=estagio, user=request.user)
        if form.is_valid():
            estagio_instance = form.save()
            
            template_path = str(os.path.join(settings.BASE_DIR, "dashboard", "templates", "docs", "TceuTemplate.docx"))
            
            output_pdf_path = preencher_tceu(estagio_instance, template_path)
            
            if output_pdf_path and os.path.exists(str(output_pdf_path)): 
                
                relative_path = str(output_pdf_path).replace(str(settings.MEDIA_ROOT), '').lstrip('/')
                estagio_instance.pdf_termo.name = relative_path
                estagio_instance.save()

                with open(str(output_pdf_path), 'rb') as fh:  
                    response = HttpResponse(fh.read(), content_type="application/pdf")
                    filename = os.path.basename(str(output_pdf_path))   
                    response['Content-Disposition'] = f'attachment; filename="{filename}"'
                    
                    # Adicionando mensagem de sucesso antes do retorno
                    messages.success(request, "Estágio salvo com sucesso!")
                    return response
            else:
                messages.error(request, "O documento PDF não pôde ser gerado.")
                raise Http404("O documento PDF não pôde ser gerado.")
        else:
            messages.error(request, "Erro ao salvar estágio.")
    else:
        form = EstagioCadastroForm(instance=estagio, user=request.user)

    return render(request, template, {"form": form, "estagio": estagio})


@login_required
def add_estagios(request):
    return processar_form_estagio(request)


@login_required
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
    print("Documento Path:", documento_path)
    print("Documento URL:", documento_url)

    return render(
        request,
        "details.html",
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


def get_supervisores(request):
    empresa_id = request.GET.get("empresa_id")
    if empresa_id:
        supervisores = Supervisor.objects.filter(empresa_id=empresa_id).values(
            "id", "nome_completo"
        )
        return JsonResponse(list(supervisores), safe=False)
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