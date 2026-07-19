from django.db import models


class Groupe(models.Model):
    """Un groupe d'etudiants (ex: 'Groupe A', 'L2 Info - Groupe B')."""
    nom = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Groupe"
        verbose_name_plural = "Groupes"
        ordering = ['nom']

    def __str__(self):
        return self.nom


class Periode(models.Model):
    """Un trimestre, semestre ou toute autre periode d'evaluation."""
    nom = models.CharField(max_length=100, help_text="Ex: Trimestre 1, Semestre 1 2025-2026")
    date_debut = models.DateField(null=True, blank=True)
    date_fin = models.DateField(null=True, blank=True)
    actif = models.BooleanField(default=True, help_text="Periode en cours")

    class Meta:
        verbose_name = "Periode"
        verbose_name_plural = "Periodes"
        ordering = ['-date_debut', 'nom']

    def __str__(self):
        return self.nom
