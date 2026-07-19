from django.contrib.auth.models import User
from django.db import models


class Profil(models.Model):
    """
    Informations complementaires sur chaque utilisateur.
    Les comptes ne sont PAS auto-crees : c'est l'admin (toi) qui cree
    chaque etudiant depuis /admin/.
    """

    ETUDIANT = 'etudiant'
    ADMIN = 'admin'
    ROLES = [
        (ETUDIANT, 'Etudiant'),
        (ADMIN, 'Administrateur / Enseignant'),
    ]

    utilisateur = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil')
    role = models.CharField(max_length=10, choices=ROLES, default=ETUDIANT)
    classe = models.CharField(max_length=100, blank=True, help_text="Ex: L2 Info, Groupe A...")
    groupe = models.ForeignKey(
        'scolarite.Groupe', on_delete=models.SET_NULL, null=True, blank=True, related_name='etudiants',
    )
    numero_telephone = models.CharField(
        max_length=20, blank=True,
        help_text="Format international recommande, ex: +2250700000000 (necessaire pour SMS/WhatsApp).",
    )
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Profil"
        verbose_name_plural = "Profils"

    def __str__(self):
        return f"{self.utilisateur.get_full_name() or self.utilisateur.username} ({self.get_role_display()})"

    @property
    def est_admin(self):
        return self.role == self.ADMIN or self.utilisateur.is_staff
