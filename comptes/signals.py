from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profil


@receiver(post_save, sender=User)
def creer_ou_maj_profil(sender, instance, created, **kwargs):
    """Cree automatiquement un Profil quand un User est cree (ex: via /admin/)."""
    if created:
        Profil.objects.get_or_create(
            utilisateur=instance,
            defaults={'role': Profil.ADMIN if instance.is_staff else Profil.ETUDIANT},
        )
