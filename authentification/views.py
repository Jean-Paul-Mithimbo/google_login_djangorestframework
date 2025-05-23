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


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = settings.GOOGLE_OAUTH_CALLBACK_URL
    client_class = OAuth2Client


class GoogleLoginCallback(APIView):
    def get(self, request, *args, **kwargs):
        code = request.GET.get("code")

        if not code:
            return Response({"detail": "Code OAuth manquant"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            base_url = getattr(settings, "BASE_URL", "http://localhost:8000")
            token_endpoint_url = urljoin(base_url, reverse("google_login"))

            # ✅ Envoi au format JSON
            response = requests.post(token_endpoint_url, json={
                "code": code,
                "redirect_uri": settings.GOOGLE_OAUTH_CALLBACK_URL
            }, headers={
                "Content-Type": "application/json"
            })

            if response.status_code != 200:
                return Response({
                    "detail": "Échec de la connexion avec Google",
                    "status_code": response.status_code,
                    "error": response.text[:300]
                }, status=response.status_code)

            return Response(response.json(), status=status.HTTP_200_OK)

        except requests.RequestException as e:
            return Response({
                "detail": "Erreur réseau lors de la connexion avec Google",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({
                "detail": "Une erreur inattendue s'est produite",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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