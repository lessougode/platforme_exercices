from decimal import Decimal

from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.db import models

EXTENSIONS_CONSIGNE = ['pdf', 'doc', 'docx']
EXTENSIONS_RENDU = ['pdf', 'doc', 'docx', 'py', 'jpg', 'jpeg', 'png']


class Devoir(models.Model):
    """Un travail donne par l'admin, que les etudiants doivent rendre."""
    titre = models.CharField(max_length=200)
    consignes = models.TextField(blank=True)
    fichier_consigne = models.FileField(
        upload_to='devoirs/consignes/%Y/%m/',
        validators=[FileExtensionValidator(EXTENSIONS_CONSIGNE)],
        null=True, blank=True,
    )
    periode = models.ForeignKey(
        'scolarite.Periode', on_delete=models.SET_NULL, null=True, blank=True, related_name='devoirs',
    )
    coefficient = models.DecimalField(
        max_digits=4, decimal_places=2, default=Decimal('1.00'),
        help_text="Coefficient utilise dans le calcul de la moyenne du bulletin.",
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_limite = models.DateTimeField(null=True, blank=True)
    actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Devoir"
        verbose_name_plural = "Devoirs"
        ordering = ['-date_creation']

    def __str__(self):
        return self.titre


class RenduDevoir(models.Model):
    """Ce qu'un etudiant envoie en reponse a un Devoir : un fichier et/ou un texte redige
    directement (utile pour les matieres litteraires, sans fichier a joindre)."""
    devoir = models.ForeignKey(Devoir, on_delete=models.CASCADE, related_name='rendus')
    etudiant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rendus')
    fichier = models.FileField(
        upload_to='devoirs/rendus/%Y/%m/',
        validators=[FileExtensionValidator(EXTENSIONS_RENDU)],
        null=True, blank=True,
    )
    texte_reponse = models.TextField(
        blank=True, help_text="Reponse redigee directement (optionnelle si un fichier est joint).",
    )
    commentaire_etudiant = models.TextField(blank=True)
    date_soumission = models.DateTimeField(auto_now_add=True)

    # Correction par l'admin
    note = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text="Note sur 20 (utilisee telle quelle dans le calcul du bulletin).",
    )
    commentaire_admin = models.TextField(blank=True)
    fichier_correction = models.FileField(
        upload_to='devoirs/corrections/%Y/%m/', null=True, blank=True
    )
    corrige = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Rendu de devoir"
        verbose_name_plural = "Rendus de devoirs"
        ordering = ['-date_soumission']
        unique_together = ('devoir', 'etudiant')

    def __str__(self):
        return f"{self.etudiant.username} - {self.devoir.titre}"
