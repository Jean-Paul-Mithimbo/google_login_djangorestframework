from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from django.conf import settings

# google logn callback
from urllib.parse import urljoin

import requests
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# login page
from django.conf import settings
from django.shortcuts import render
from django.views import View

from django.urls import reverse
from urllib.parse import urljoin
import requests
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from allauth.socialaccount.models import SocialAccount


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = settings.GOOGLE_OAUTH_CALLBACK_URL
    # client_class = OAuth2Client



class GoogleLoginCallback(APIView):
    def get(self, request, *args, **kwargs):
        code = request.GET.get("code")
        if not code:
            return Response({"detail": "Code OAuth manquant"}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Échange le code contre un access_token Google
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
            "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_OAUTH_CALLBACK_URL,
            "grant_type": "authorization_code",
        }
        token_response = requests.post(token_url, data=data)
        if token_response.status_code != 200:
            return Response({
                "detail": "Erreur lors de l'échange du code avec Google",
                "status_code": token_response.status_code,
                "error": token_response.text[:300]
            }, status=status.HTTP_400_BAD_REQUEST)

        access_token = token_response.json().get("access_token")
        if not access_token:
            return Response({
                "detail": "Access token manquant dans la réponse Google",
                "error": token_response.text[:300]
            }, status=status.HTTP_400_BAD_REQUEST)

        # 2. Récupère les infos utilisateur Google
        user_info = requests.get(
            "https://www.googleapis.com/oauth2/v1/userinfo",
            params={"access_token": access_token}
        ).json()
        email = user_info.get("email")
        if not email:
            return Response({"detail": "Impossible de récupérer l'email Google"}, status=400)

        # 3. Récupère ou crée l'utilisateur avec toutes les infos utiles
        User = get_user_model()
        defaults = {
            "username": email.split("@")[0],
            "role": "user",
            "first_name": user_info.get("given_name", ""),
            "last_name": user_info.get("family_name", ""),
        }
        user, created = User.objects.get_or_create(email=email, defaults=defaults)

        # Si l'utilisateur existe déjà, on met à jour les infos (sauf le rôle)
        if not created:
            updated = False
            if user.first_name != user_info.get("given_name", ""):
                user.first_name = user_info.get("given_name", "")
                updated = True
            if user.last_name != user_info.get("family_name", ""):
                user.last_name = user_info.get("family_name", "")
                updated = True
            if user.username != email.split("@")[0]:
                user.username = email.split("@")[0]
                updated = True
            if updated:
                user.save()

        # 4. Lier le SocialAccount à la première connexion
        if created:
            SocialAccount.objects.create(user=user, provider="google", uid=user_info.get("id"))

        # 5. Génère les tokens JWT
        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)
        refresh = str(refresh)

        # 6. Retourne la réponse
        return Response({
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role,
            },
            "access": access,
            "refresh": refresh,
        })

class LoginPage(View):
    def get(self, request, *args, **kwargs):
        return render(
            request,
            "login.html",
            {
                "google_callback_uri": settings.GOOGLE_OAUTH_CALLBACK_URL,
                "google_client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
            },
        )





# class GoogleLoginCallback(APIView):
#     def get(self, request, *args, **kwargs):
#         code = request.GET.get("code")
#         if not code:
#             return Response({"detail": "Code OAuth manquant"}, status=status.HTTP_400_BAD_REQUEST)

#         # 1. Échange le code contre un access_token auprès de Google
#         token_url = "https://oauth2.googleapis.com/token"
#         data = {
#             "code": code,
#             "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
#             "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
#             "redirect_uri": settings.GOOGLE_OAUTH_CALLBACK_URL,
#             "grant_type": "authorization_code",
#         }
#         token_response = requests.post(token_url, data=data)
#         if token_response.status_code != 200:
#             return Response({
#                 "detail": "Erreur lors de l'échange du code avec Google",
#                 "status_code": token_response.status_code,
#                 "error": token_response.text[:300]
#             }, status=status.HTTP_400_BAD_REQUEST)

#         access_token = token_response.json().get("access_token")
#         if not access_token:
#             return Response({
#                 "detail": "Access token manquant dans la réponse Google",
#                 "error": token_response.text[:300]
#             }, status=status.HTTP_400_BAD_REQUEST)

#         # 2. Récupère les infos utilisateur Google
#         user_info = requests.get(
#             "https://www.googleapis.com/oauth2/v1/userinfo",
#             params={"access_token": access_token}
#         ).json()
#         email = user_info.get("email")
#         if not email:
#             return Response({"detail": "Impossible de récupérer l'email Google"}, status=400)

#         # 3. Récupère ou crée l'utilisateur
#         User = get_user_model()
#         user, created = User.objects.get_or_create(email=email, defaults={
#             "username": email.split("@")[0],
#             "role": "user",
#         })

#         # 4. (Optionnel) Lier le SocialAccount
#         if created:
#             SocialAccount.objects.create(user=user, provider="google", uid=user_info.get("id"))

#         # 5. Génère les tokens JWT
#         refresh = RefreshToken.for_user(user)
#         access = str(refresh.access_token)
#         refresh = str(refresh)

#         # 6. Retourne la réponse custom
#         return Response({
#             "user": {
#                 "id": user.id,
#                 "username": user.username,
#                 "email": user.email,
#                 "role": user.role,
#             },
#             "access": access,
#             "refresh": refresh,
#         })


# class LoginPage(View):
#     def get(self, request, *args, **kwargs):
#         return render(
#             request,
#             "login.html",
#             {
#                 "google_callback_uri": settings.GOOGLE_OAUTH_CALLBACK_URL,
#                 "google_client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
#             },
#         )