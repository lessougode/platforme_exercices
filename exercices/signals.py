from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import ReponseEtudiant


@receiver(post_save, sender=ReponseEtudiant)
def recalculer_score_tentative(sender, instance, **kwargs):
    """Quand une reponse est enregistree/modifiee (ex: note manuelle saisie
    par l'admin sur une question 'reponse libre'), on recalcule le score total."""
    instance.tentative.recalculer_score()
