from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Choix, ElementAppariement, Exercice, Question,
    ReponseEtudiant, TentativeExercice, Trou,
)


class ChoixInline(admin.TabularInline):
    """A remplir uniquement si le type de question est QCM."""
    model = Choix
    extra = 4
    fields = ('texte', 'image', 'est_correct', 'ordre')


class ElementAppariementInline(admin.TabularInline):
    """A remplir uniquement si le type de question est Appariement."""
    model = ElementAppariement
    extra = 3
    fields = ('element_gauche', 'image_gauche', 'element_droite', 'ordre')


class TrouInline(admin.TabularInline):
    """A remplir uniquement si le type de question est Texte a trous.
    Utiliser ___1___, ___2___... dans l'enonce, et une ligne par numero ici."""
    model = Trou
    extra = 3
    fields = ('position', 'reponses_acceptees')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('exercice', 'ordre', 'type_question', 'type_reponse_qcm', 'enonce_court', 'a_une_image', 'points')
    list_filter = ('exercice', 'type_question')
    fields = ('exercice', 'type_question', 'type_reponse_qcm', 'enonce', 'image', 'points', 'ordre')
    inlines = [ChoixInline, ElementAppariementInline, TrouInline]

    def enonce_court(self, obj):
        return obj.enonce[:60]
    enonce_court.short_description = "Enonce"

    def a_une_image(self, obj):
        return bool(obj.image)
    a_une_image.boolean = True
    a_une_image.short_description = "Image"


class QuestionInline(admin.StackedInline):
    """Permet d'ajouter des questions directement depuis la page Exercice.
    Pour saisir les choix / paires / trous / image en detail, ouvrir ensuite la Question elle-meme
    (un lien 'Modifier' apparait une fois l'exercice enregistre)."""
    model = Question
    extra = 1
    fields = ('type_question', 'type_reponse_qcm', 'enonce', 'points', 'ordre')
    show_change_link = True


@admin.register(Exercice)
class ExerciceAdmin(admin.ModelAdmin):
    list_display = ('titre', 'type_exercice', 'matiere', 'periode', 'groupe', 'classe', 'filiere', 'coefficient', 'nombre_points', 'actif', 'date_creation')
    list_filter = ('type_exercice', 'matiere', 'periode', 'groupe', 'classe', 'filiere', 'actif')
    search_fields = ('titre', 'description')
    fields = ('titre', 'description', 'type_exercice', 'matiere', 'periode', 'groupe', 'classe', 'filiere', 'coefficient', 'image_support', 'texte_support', 'actif', 'date_limite')
    inlines = [QuestionInline]

    def nombre_points(self, obj):
        return obj.total_points
    nombre_points.short_description = "Points totaux"


class ReponseEtudiantInline(admin.TabularInline):
    """Affiche la copie de l'etudiant depuis la Tentative, et permet de noter
    manuellement les questions de type 'reponse libre' (redaction)."""
    model = ReponseEtudiant
    extra = 0
    can_delete = False
    fields = ('question', 'apercu_reponse', 'points_obtenus')
    readonly_fields = ('question', 'apercu_reponse')

    def apercu_reponse(self, obj):
        if not obj.pk:
            return "-"
        q = obj.question
        donnees = obj.donnees_reponse or {}
        if q.type_question == Question.REPONSE_LIBRE:
            texte = donnees.get('texte', '')
            return format_html('<div style="white-space:pre-line;max-width:500px;">{}</div>', texte or "(vide)")
        if q.type_question == Question.QCM:
            ids = donnees.get('choix', [])
            textes = [c.texte for c in q.choix.all() if c.id in ids]
            return ", ".join(textes) or "(aucune reponse)"
        if q.type_question == Question.APPARIEMENT:
            paires = donnees.get('paires', {})
            return format_html('<br>'.join(f"{k} : {v}" for k, v in paires.items()) or "(aucune reponse)")
        if q.type_question == Question.TEXTE_TROU:
            trous = donnees.get('trous', {})
            return format_html('<br>'.join(f"Trou {k} : {v}" for k, v in trous.items()) or "(aucune reponse)")
        return "-"
    apercu_reponse.short_description = "Reponse de l'etudiant"


@admin.register(TentativeExercice)
class TentativeExerciceAdmin(admin.ModelAdmin):
    list_display = ('etudiant', 'exercice', 'score_obtenu', 'necessite_correction', 'termine', 'date_soumission')
    list_filter = ('exercice', 'termine')
    search_fields = ('etudiant__username',)
    inlines = [ReponseEtudiantInline]

    def necessite_correction(self, obj):
        return obj.exercice.a_correction_manuelle
    necessite_correction.boolean = True
    necessite_correction.short_description = "A corriger manuellement"


admin.site.register(ReponseEtudiant)
