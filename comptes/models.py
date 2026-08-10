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
    avatar = models.ImageField(
        upload_to='comptes/avatars/%Y/%m/', null=True, blank=True,
        verbose_name="Photo de profil",
        help_text="Si aucune photo n'est ajoutée, l'avatar par défaut du site reste utilisé.",
    )
    classe = models.ForeignKey(
        'scolarite.Classe', on_delete=models.SET_NULL, null=True, blank=True, related_name='eleves',
        verbose_name="Classe",
        help_text="Pour un élève de primaire / secondaire.",
    )
    filiere = models.ForeignKey(
        'scolarite.Filiere', on_delete=models.SET_NULL, null=True, blank=True, related_name='etudiants',
        verbose_name="Filière",
        help_text="Pour un étudiant d'université.",
    )
    groupe = models.ForeignKey(
        'scolarite.Groupe', on_delete=models.SET_NULL, null=True, blank=True, related_name='etudiants',
    )
    periode = models.ForeignKey(
        'scolarite.Periode', on_delete=models.SET_NULL, null=True, blank=True, related_name='etudiants',
        verbose_name="Période",
    )
    cours = models.ManyToManyField(
        'cours.Cours', blank=True, related_name='etudiants',
        verbose_name="Cours suivis",
        help_text="Cours auxquels cet élève est inscrit.",
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
