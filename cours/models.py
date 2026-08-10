from django.core.validators import FileExtensionValidator
from django.db import models

EXTENSIONS_AUTORISEES = ['pdf', 'doc', 'docx', 'mp4', 'mov', 'avi', 'mkv', 'mp3', 'wav', 'ogg', 'm4a']


class Matiere(models.Model):
    """Regroupement optionnel des cours par matiere/theme."""
    nom = models.CharField(max_length=150)

    class Meta:
        verbose_name = "Matiere"
        verbose_name_plural = "Matieres"

    def __str__(self):
        return self.nom


class Cours(models.Model):
    PDF = 'pdf'
    WORD = 'word'
    VIDEO = 'video'
    AUDIO = 'audio'
    TYPES = [
        (PDF, 'PDF'),
        (WORD, 'Document Word'),
        (VIDEO, 'Video'),
        (AUDIO, 'Audio'),
    ]

    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    matiere = models.ForeignKey(Matiere, on_delete=models.SET_NULL, null=True, blank=True, related_name='cours')
    periode = models.ForeignKey(
        'scolarite.Periode', on_delete=models.SET_NULL, null=True, blank=True, related_name='cours',
        verbose_name="Période",
    )
    groupe = models.ForeignKey(
        'scolarite.Groupe', on_delete=models.SET_NULL, null=True, blank=True, related_name='cours',
        verbose_name="Groupe",
    )
    classe = models.ForeignKey(
        'scolarite.Classe', on_delete=models.SET_NULL, null=True, blank=True, related_name='cours',
        verbose_name="Classe",
        help_text="Pour organiser/filtrer (primaire / secondaire).",
    )
    filiere = models.ForeignKey(
        'scolarite.Filiere', on_delete=models.SET_NULL, null=True, blank=True, related_name='cours',
        verbose_name="Filière",
        help_text="Pour organiser/filtrer (université).",
    )
    type_fichier = models.CharField(max_length=10, choices=TYPES)
    fichier = models.FileField(
        upload_to='cours/%Y/%m/',
        validators=[FileExtensionValidator(EXTENSIONS_AUTORISEES)],
    )
    date_ajout = models.DateTimeField(auto_now_add=True)
    visible = models.BooleanField(default=True, help_text="Visible par les etudiants")

    class Meta:
        verbose_name = "Cours"
        verbose_name_plural = "Cours"
        ordering = ['-date_ajout']

    def __str__(self):
        return self.titre
