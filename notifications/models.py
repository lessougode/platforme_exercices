from django.contrib.auth.models import User
from django.db import models


class Notification(models.Model):
    EMAIL = 'email'
    SMS = 'sms'
    WHATSAPP = 'whatsapp'
    CANAUX = [
        (EMAIL, 'Email'),
        (SMS, 'SMS'),
        (WHATSAPP, 'WhatsApp'),
    ]

    BROUILLON = 'brouillon'
    ENVOYE = 'envoye'
    ENVOYE_PARTIEL = 'envoye_partiel'
    ERREUR = 'erreur'
    STATUTS = [
        (BROUILLON, 'Brouillon (pas encore envoye)'),
        (ENVOYE, 'Envoye avec succes'),
        (ENVOYE_PARTIEL, 'Envoye partiellement (voir le rapport)'),
        (ERREUR, 'Echec total'),
    ]

    objet = models.CharField(max_length=200, help_text="Utilise comme sujet pour l'email.")
    message = models.TextField()
    canal = models.CharField(max_length=10, choices=CANAUX, default=EMAIL)

    destinataires = models.ManyToManyField(
        User, blank=True, related_name='notifications_recues',
        help_text="Selectionne directement des etudiants...",
    )
    groupe_cible = models.ForeignKey(
        'scolarite.Groupe', on_delete=models.SET_NULL, null=True, blank=True,
        help_text="...et/ou choisis un groupe entier (s'ajoute aux destinataires ci-dessus).",
    )

    envoye_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_envoi = models.DateTimeField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUTS, default=BROUILLON)
    rapport_envoi = models.TextField(blank=True, help_text="Detail des envois reussis/echoues, rempli automatiquement.")

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-date_creation']

    def __str__(self):
        return f"[{self.get_canal_display()}] {self.objet}"

    def liste_destinataires(self):
        """Tous les destinataires effectifs : selection directe + groupe cible."""
        destinataires = set(self.destinataires.all())
        if self.groupe_cible:
            destinataires |= set(User.objects.filter(profil__groupe=self.groupe_cible))
        return destinataires
