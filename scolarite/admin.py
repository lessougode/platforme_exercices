from django.contrib import admin

from .models import Classe, ConfigurationSite, Enseignant, Etablissement, Filiere, Groupe, Periode

@admin.register(Groupe)
class GroupeAdmin(admin.ModelAdmin):
    list_display = ("nom",)
    search_fields = ("nom",)

@admin.register(Classe)
class ClasseAdmin(admin.ModelAdmin):
    list_display = ("nom",)
    search_fields = ("nom",)

@admin.register(Filiere)
class FiliereAdmin(admin.ModelAdmin):
    list_display = ("nom",)
    search_fields = ("nom",)

@admin.register(Enseignant)
class EnseignantAdmin(admin.ModelAdmin):
    list_display = ("nom_complet", "email", "telephone")
    search_fields = ("nom_complet", "email")
    filter_horizontal = ("cours", "classes")

@admin.register(Periode)
class PeriodeAdmin(admin.ModelAdmin):
    list_display = (
    "nom",
    "type_periode",
    "annee_scolaire",
    "date_debut",
    "date_fin",
    "actif",
    )


    list_filter = (
        "type_periode",
        "actif",
    )

    search_fields = (
        "nom",
    )

@admin.register(ConfigurationSite)
class ConfigurationSiteAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "titre_site",
        "logo",
        "image_visiteur",
        "image_utilisateur",
    )

    def has_add_permission(self, request):
        # Un seul enregistrement de configuration est autorisé.
        return not ConfigurationSite.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # L'unique configuration du site ne doit jamais être supprimée.
        return False


@admin.register(Etablissement)
class EtablissementAdmin(admin.ModelAdmin):
    list_display = ("nom_affiche", "ville", "quartier", "telephone", "email", "code_ou_decision")

    def nom_affiche(self, obj):
        return obj.nom or "(Clique ici pour renseigner l'établissement)"
    nom_affiche.short_description = "Nom de l'établissement"

    def has_add_permission(self, request):
        # Un seul établissement pour l'instant (multi-établissement prévu plus tard).
        return not Etablissement.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
