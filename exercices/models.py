from decimal import Decimal, ROUND_HALF_UP

from django.contrib.auth.models import User
from django.db import models


def arrondir(valeur):
    """Arrondit un score au centieme le plus proche et renvoie un Decimal."""
    if not isinstance(valeur, Decimal):
        valeur = Decimal(str(valeur))
    return valeur.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


class Exercice(models.Model):
    FIXATION = 'fixation'
    APPROFONDISSEMENT = 'approfondissement'
    REFLEXION = 'reflexion'
    TYPES_EXERCICE = [
        (FIXATION, 'Exercice de fixation'),
        (APPROFONDISSEMENT, "Exercice d'approfondissement"),
        (REFLEXION, 'Exercice de reflexion'),
    ]

    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    type_exercice = models.CharField(max_length=20, choices=TYPES_EXERCICE)
    matiere = models.ForeignKey('cours.Matiere', on_delete=models.SET_NULL, null=True, blank=True)
    periode = models.ForeignKey(
        'scolarite.Periode', on_delete=models.SET_NULL, null=True, blank=True, related_name='exercices',
    )
    groupe = models.ForeignKey(
        'scolarite.Groupe', on_delete=models.SET_NULL, null=True, blank=True, related_name='exercices',
        verbose_name="Groupe",
    )
    classe = models.ForeignKey(
        'scolarite.Classe', on_delete=models.SET_NULL, null=True, blank=True, related_name='exercices',
        verbose_name="Classe",
        help_text="Pour organiser/filtrer (primaire / secondaire).",
    )
    filiere = models.ForeignKey(
        'scolarite.Filiere', on_delete=models.SET_NULL, null=True, blank=True, related_name='exercices',
        verbose_name="Filière",
        help_text="Pour organiser/filtrer (université).",
    )
    coefficient = models.DecimalField(
        max_digits=4, decimal_places=2, default=Decimal('1.00'),
        help_text="Coefficient utilise dans le calcul de la moyenne du bulletin.",
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    actif = models.BooleanField(default=True, help_text="Visible / accessible aux etudiants")
    date_limite = models.DateTimeField(null=True, blank=True)

    # Support commun affiche AU-DESSUS de toutes les questions : utile pour une image
    # de reference (ex: courbe en sciences) ou un texte de reference (ex: extrait
    # litteraire) sur lequel portent plusieurs questions de l'exercice.
    image_support = models.ImageField(
        upload_to='exercices/supports/%Y/%m/', null=True, blank=True,
        help_text="Image commune a l'exercice (ex: courbe, schema), affichee avant les questions.",
    )
    texte_support = models.TextField(
        blank=True,
        help_text="Texte de reference commun a l'exercice (ex: extrait litteraire a analyser), affiche avant les questions.",
    )

    class Meta:
        verbose_name = "Exercice"
        verbose_name_plural = "Exercices"
        ordering = ['-date_creation']

    def __str__(self):
        return f"[{self.get_type_exercice_display()}] {self.titre}"

    @property
    def total_points(self):
        return self.questions.aggregate(total=models.Sum('points'))['total'] or Decimal('0')

    @property
    def a_correction_manuelle(self):
        """True si l'exercice contient au moins une question a corriger manuellement (reponse libre)."""
        return self.questions.filter(type_question=Question.REPONSE_LIBRE).exists()


class Question(models.Model):
    QCM = 'qcm'
    APPARIEMENT = 'appariement'
    TEXTE_TROU = 'texte_trou'
    REPONSE_LIBRE = 'reponse_libre'
    TYPES_QUESTION = [
        (QCM, 'QCM'),
        (APPARIEMENT, 'Appariement'),
        (TEXTE_TROU, 'Texte a trous (closure)'),
        (REPONSE_LIBRE, 'Reponse libre / redaction (notee manuellement)'),
    ]

    UNIQUE = 'unique'
    MULTIPLE = 'multiple'
    TYPES_REPONSE_QCM = [
        (UNIQUE, 'Une seule bonne reponse (boutons radio)'),
        (MULTIPLE, 'Plusieurs bonnes reponses possibles (cases a cocher)'),
    ]

    exercice = models.ForeignKey(Exercice, on_delete=models.CASCADE, related_name='questions')
    type_question = models.CharField(max_length=20, choices=TYPES_QUESTION)
    type_reponse_qcm = models.CharField(
        max_length=10, choices=TYPES_REPONSE_QCM, default=UNIQUE,
        help_text="Uniquement utilise si le type de question est QCM.",
    )
    enonce = models.TextField(
        help_text="Pour un texte a trous, utiliser ___1___, ___2___, ... comme marqueurs de trou."
    )
    image = models.ImageField(
        upload_to='exercices/questions/%Y/%m/', null=True, blank=True,
        help_text="Image illustrant l'enonce (schema, formule mathematique, graphique...).",
    )
    points = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('1.00'))
    ordre = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Question"
        verbose_name_plural = "Questions"
        ordering = ['ordre', 'id']

    def __str__(self):
        return f"Q{self.ordre} - {self.enonce[:50]}"


class Choix(models.Model):
    """Option de reponse pour une question de type QCM."""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choix')
    texte = models.CharField(max_length=300, blank=True, help_text="Peut rester vide si une image suffit.")
    image = models.ImageField(
        upload_to='exercices/choix/%Y/%m/', null=True, blank=True,
        help_text="Image illustrant cette option (formule, schema...).",
    )
    est_correct = models.BooleanField(default=False)
    ordre = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Choix (QCM)"
        verbose_name_plural = "Choix (QCM)"
        ordering = ['ordre', 'id']

    def __str__(self):
        return self.texte or f"(image #{self.id})"


class ElementAppariement(models.Model):
    """Une paire a associer pour une question de type Appariement.
    Cote etudiant, l'element de gauche est fixe (texte et/ou image) et l'element de
    droite est choisi dans une liste deroulante (comme sur Moodle)."""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='paires')
    element_gauche = models.CharField(max_length=300, blank=True)
    image_gauche = models.ImageField(
        upload_to='exercices/appariement/%Y/%m/', null=True, blank=True,
        help_text="Image a la place ou en plus du texte de gauche (ex: formule a associer).",
    )
    element_droite = models.CharField(max_length=300, help_text="Correspondance correcte")
    ordre = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Paire d'appariement"
        verbose_name_plural = "Paires d'appariement"
        ordering = ['ordre', 'id']

    def __str__(self):
        return f"{self.element_gauche} -> {self.element_droite}"


class Trou(models.Model):
    """Reponse attendue pour chaque marqueur ___N___ d'une question texte a trous.
    Chaque trou est note independamment (comme Moodle : note partielle possible).
    Plusieurs reponses acceptees peuvent etre separees par '|' (ex: 'difficulty|challenge')."""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='trous')
    position = models.PositiveIntegerField(help_text="Numero du marqueur ___N___ correspondant")
    reponses_acceptees = models.CharField(
        max_length=300,
        help_text="Reponse(s) correcte(s). Separer par '|' si plusieurs formulations sont acceptees.",
    )

    class Meta:
        verbose_name = "Trou (texte a trous)"
        verbose_name_plural = "Trous (texte a trous)"
        ordering = ['position']

    def __str__(self):
        return f"Trou {self.position}: {self.reponses_acceptees}"

    def est_correct(self, reponse_donnee):
        reponse_donnee = (reponse_donnee or '').strip().lower()
        acceptees = [r.strip().lower() for r in self.reponses_acceptees.split('|')]
        return reponse_donnee in acceptees


class TentativeExercice(models.Model):
    """Une soumission d'un etudiant pour un exercice donne."""
    etudiant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tentatives')
    exercice = models.ForeignKey(Exercice, on_delete=models.CASCADE, related_name='tentatives')
    date_debut = models.DateTimeField(auto_now_add=True)
    date_soumission = models.DateTimeField(null=True, blank=True)
    termine = models.BooleanField(default=False)
    score_obtenu = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0'))

    class Meta:
        verbose_name = "Tentative d'exercice"
        verbose_name_plural = "Tentatives d'exercice"
        ordering = ['-date_debut']

    def __str__(self):
        return f"{self.etudiant.username} - {self.exercice.titre} ({self.score_obtenu}/{self.exercice.total_points})"

    def recalculer_score(self):
        total = self.reponses.aggregate(total=models.Sum('points_obtenus'))['total'] or Decimal('0')
        self.score_obtenu = arrondir(total)
        self.save(update_fields=['score_obtenu'])


class ReponseEtudiant(models.Model):
    """Reponse d'un etudiant a UNE question, dans le cadre d'une tentative."""
    tentative = models.ForeignKey(TentativeExercice, on_delete=models.CASCADE, related_name='reponses')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    # Stockage generique : liste d'ids de choix (QCM), mapping paire_id->reponse (appariement),
    # mapping position->reponse (texte a trous), ou {'texte': ...} (reponse libre).
    donnees_reponse = models.JSONField(default=dict, blank=True)
    points_obtenus = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0'))

    class Meta:
        verbose_name = "Reponse etudiant"
        verbose_name_plural = "Reponses etudiant"
        unique_together = ('tentative', 'question')

    def __str__(self):
        return f"Reponse de {self.tentative.etudiant.username} - Q{self.question.ordre}"

    @property
    def texte_libre(self):
        return (self.donnees_reponse or {}).get('texte', '')
