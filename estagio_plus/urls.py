# estagio_plus/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    
    # INCLUA AS URLs DO ALLAUTH NA RAIZ
    # Isso fará com que /login/, /signup/, /logout/ etc. funcionem diretamente.
    path("", include("allauth.urls")), 
    
    # INCLUA AS URLs DO SEU APP 'BASE' PARA O PERFIL
    # Esta rota /accounts/profile/ será tratada exclusivamente pelo seu app 'base'.
    # É importante que esta linha venha DEPOIS da inclusão principal do allauth,
    # mas antes de qualquer outra URL que possa tentar capturar /accounts/profile/.
    path("accounts/profile/", include("base.urls")), 
    
    # INCLUA AS URLs DO DASHBOARD SOB UM PREFIXO CLARO
    path("dashboard/", include("dashboard.urls")),
    
    # INCLUA AS URLs DO HOME (VALIDATE) SOB UM PREFIXO CLARO
    # Pelo seu exemplo anterior, parece que "validate/" é o prefixo para o app 'home'.
    path("validate/", include("home.urls")), 
    
    # Remova a linha path('') vazia se ela não tiver um propósito, como você já sugeriu.
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)