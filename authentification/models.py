from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('user', 'Utilisateur'),
        ('admin', 'Administrateur'),
        # Ajoute d'autres rôles si besoin
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')