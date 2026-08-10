from django.db import models

class Groupe(models.Model):
    """Un groupe d'étudiants."""

    nom = models.CharField(
        max_length=100,
        unique=True
    )

    class Meta:
        verbose_name = "Groupe"
        verbose_name_plural = "Groupes"
        ordering = ["nom"]

    def __str__(self):
        return self.nom


class Classe(models.Model):
    """Une classe (primaire / secondaire), ex : CM2, 6ème A, Terminale D."""

    nom = models.CharField(
        max_length=100,
        unique=True,
        help_text="Ex : CM2, 6ème A, Terminale D"
    )

    class Meta:
        verbose_name = "Classe"
        verbose_name_plural = "Classes"
        ordering = ["nom"]

    def __str__(self):
        return self.nom


class Filiere(models.Model):
    """Une filière (université), ex : Génie Informatique, Droit privé."""

    nom = models.CharField(
        max_length=150,
        unique=True,
        help_text="Ex : Génie Informatique, Droit privé"
    )

    class Meta:
        verbose_name = "Filière"
        verbose_name_plural = "Filières"
        ordering = ["nom"]

    def __str__(self):
        return self.nom


class Periode(models.Model):
    """Une période d'évaluation (trimestre ou semestre)."""

    TRIMESTRE = "trimestre"
    SEMESTRE = "semestre"
    TYPES_PERIODE = [
        (TRIMESTRE, "Trimestre (primaire / secondaire)"),
        (SEMESTRE, "Semestre (université)"),
    ]

    type_periode = models.CharField(
        max_length=10,
        choices=TYPES_PERIODE,
        null=True,
        blank=True,
        verbose_name="Type de période",
        help_text="Trimestre (primaire/secondaire) ou Semestre (université)."
    )

    nom = models.CharField(
        max_length=100,
        help_text="Ex : Trimestre 1, Semestre 1 2025-2026"
    )

    annee_scolaire = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Année scolaire / académique",
        help_text="Ex : 2025-2026"
    )

    date_debut = models.DateField(
        null=True,
        blank=True
    )

    date_fin = models.DateField(
        null=True,
        blank=True
    )

    actif = models.BooleanField(
        default=True,
        help_text="Période en cours"
    )

    class Meta:
        verbose_name = "Période"
        verbose_name_plural = "Périodes"
        ordering = ["-date_debut", "nom"]

    def __str__(self):
        return self.nom


class Enseignant(models.Model):
    """Un enseignant, lié aux cours qu'il donne et aux classes qu'il a en charge.
    Un enseignant peut enseigner plusieurs cours et avoir plusieurs classes."""

    nom_complet = models.CharField(max_length=200, verbose_name="Nom complet")
    email = models.EmailField(blank=True)
    telephone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")

    cours = models.ManyToManyField(
        'cours.Cours', blank=True, related_name='enseignants',
        verbose_name="Cours enseignés",
    )
    classes = models.ManyToManyField(
        'scolarite.Classe', blank=True, related_name='enseignants',
        verbose_name="Classes en charge",
    )

    class Meta:
        verbose_name = "Enseignant"
        verbose_name_plural = "Enseignants"
        ordering = ["nom_complet"]

    def __str__(self):
        return self.nom_complet


class Etablissement(models.Model):
    """Informations sur l'établissement (école / université) qui utilise la
    plateforme. Singleton : un seul enregistrement (pk=1) doit exister,
    comme ConfigurationSite. Utiliser Etablissement.charger()."""

    nom = models.CharField(max_length=200, blank=True, verbose_name="Nom de l'établissement")
    ville = models.CharField(max_length=100, blank=True, verbose_name="Ville")
    quartier = models.CharField(max_length=100, blank=True, verbose_name="Quartier")
    telephone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    email = models.EmailField(blank=True, verbose_name="Email")
    code_ou_decision = models.CharField(
        max_length=100, blank=True,
        verbose_name="Code ou n° de décision",
        help_text="Code d'ouverture / autorisation, ou numéro de décision ministérielle.",
    )

    class Meta:
        verbose_name = "Établissement"
        verbose_name_plural = "Établissement"

    def __str__(self):
        return self.nom or "Établissement"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def charger(cls):
        instance, _ = cls.objects.get_or_create(pk=1)
        return instance


class ConfigurationSite(models.Model):
    """Configuration générale du site.

    Ce modèle est un singleton : un seul enregistrement (pk=1) doit
    exister. save() force toujours pk=1, et l'admin interdit la
    création d'un deuxième enregistrement ainsi que la suppression.
    Utiliser ConfigurationSite.charger() pour récupérer (ou créer)
    l'unique instance.
    """

    logo = models.ImageField(
        upload_to="configuration/logo/",
        null=True,
        blank=True,
        verbose_name="Logo du site"
    )

    image_visiteur = models.ImageField(
        upload_to="configuration/visiteurs/",
        null=True,
        blank=True,
        verbose_name="Image du visiteur"
    )

    image_utilisateur = models.ImageField(
        upload_to="configuration/utilisateurs/",
        null=True,
        blank=True,
        verbose_name="Image par défaut de l'utilisateur connecté"
    )

    titre_site = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Titre du site"
    )

    class Meta:
        verbose_name = "Configuration du site"
        verbose_name_plural = "Configuration du site"

    def __str__(self):
        return "Configuration générale du site"

    def save(self, *args, **kwargs):
        # Force toujours le même identifiant : un seul enregistrement possible.
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Empêche la suppression de l'unique configuration du site.
        pass

    @classmethod
    def charger(cls):
        """Retourne l'unique instance de configuration (la crée si besoin)."""
        instance, _ = cls.objects.get_or_create(pk=1)
        return instance

