import http
import json
from enum import StrEnum, auto

import requests
from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class Roles(StrEnum):
    USER = auto()
    MODERATOR = auto()
    CONTENT_MANAGER = auto()
    ADMIN = auto()
    SUPER_ADMIN = auto()


class CustomBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        login_url = settings.AUTH_API_LOGIN_URL
        me_url = settings.AUTH_API_ME_URL

        payload = {'username': username, 'password': password}
        try:
            response = requests.post(login_url, json=payload, timeout=5)

            access_token = response.json()["access_token"]

            user_response = requests.get(
                me_url,
                headers={
                    "Authorization": f"Bearer {access_token}"
                },
                timeout=5
            )

        except requests.RequestException:
            return None

        if response.status_code != http.HTTPStatus.OK:
            return None

        user_data = user_response.json()

        try:
            user, _ = User.objects.get_or_create(id=user_data['id'], )
            user.username = user_data.get('username')
            user.role = user_data.get('role')
            user.is_superuser = user_data.get('role') == Roles.SUPER_ADMIN
            user.save()
        except Exception:
            return None

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
