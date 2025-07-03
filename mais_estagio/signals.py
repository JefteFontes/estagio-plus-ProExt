from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Aluno

@receiver(post_save, sender=Aluno)
def notify_on_approval(sender, instance, created, **kwargs):
    if instance.user and instance.status and not created:
        subject = 'Seu acesso ao Sistema +Estágios foi aprovado'
        message = f"""
        Olá {instance.nome_completo},
        
        Seu cadastro no Sistema +Estágios foi aprovado pelo coordenador.
        
        Você já pode acessar o sistema usando:
        Email: {instance.email}
        Senha inicial: {instance.matricula}
        
        Recomendamos que altere sua senha após o primeiro login.
        
        Acesse o sistema em: http://127.0.0.1:8000/
        """
        send_mail(subject, message, 'noreply@seusistema.com', [instance.email])