from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("allauth.urls")), 
    path("accounts/profile/", include("home.urls")), 
    path("mais-estagio/", include("mais_estagio.urls")),
    path("validate/", include("home.urls")), 
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
