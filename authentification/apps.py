# from django.apps import AppConfig


# class AuthentificationConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'authentification'


from django.apps import AppConfig

class AuthentificationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'authentification'

    def ready(self):
        import authentification.signals