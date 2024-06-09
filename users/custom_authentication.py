from typing import Any
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.base_user import AbstractBaseUser
from django.http import HttpRequest

class CaseSensitiveEmailBackend(ModelBackend):
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        User = get_user_model()
        try:
            user = User.objects.get(email=username)
            if user.email == username:
                if user.check_password(password):
                    return {'data':user}
            else:
                return {'exception':'Email is case sensitive'}
        except User.DoesNotExist:
            return False