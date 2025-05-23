from django.contrib import admin
from django.urls import include, path, re_path

from .views import GoogleLogin, GoogleLoginCallback, LoginPage

urlpatterns = [
    # path("admin/", admin.site.urls),
    # path("login/", LoginPage.as_view(), name="login"),
    # path("api/v1/auth/", include("dj_rest_auth.urls")),
    # re_path(r"^api/v1/auth/accounts/", include("allauth.urls")),
    # path("api/v1/auth/registration/", include("dj_rest_auth.registration.urls")),
    # path("api/v1/auth/google/", GoogleLogin.as_view(), name="google_login"),
    # path(
    #     "api/v1/auth/google/callback/",
    #     GoogleLoginCallback.as_view(),
    #     name="google_login_callback",
    # ),


    path("admin/", admin.site.urls),
    path("login/", LoginPage.as_view(), name="login"),
    # Auth classique (dj-rest-auth)
    path("api/v1/auth/", include("dj_rest_auth.urls")),  # login/logout/password change/user details
    path("api/v1/auth/registration/", include("dj_rest_auth.registration.urls")),  # inscription
    # Social login
    path("api/v1/auth/google/", GoogleLogin.as_view(), name="google_login"),
    path("api/v1/auth/google/callback/", GoogleLoginCallback.as_view(), name="google_login_callback"),
    # Allauth pour gestion comptes sociaux (optionnel)
    re_path(r"^api/v1/auth/accounts/", include("allauth.urls")),
]