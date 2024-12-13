from ninja import Router
from django.contrib.auth import authenticate, login as auth_login
from pydantic import BaseModel
from django.http import JsonResponse

router = Router()

class LoginSchema(BaseModel):
    username: str
    password: str

@router.post("/login")
def login(request, data: LoginSchema):
    user = authenticate(username=data.username, password=data.password)
    if user is not None: 
        auth_login(request, user)  # Inicia a sessão do usuário
        return JsonResponse({"message": "Login successful"})
    else:
        return JsonResponse({"error": "Invalid credentials"}, status=401)
