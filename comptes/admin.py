from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Profil


class ProfilInline(admin.StackedInline):
    model = Profil
    can_delete = False
    verbose_name_plural = "Profil"
    fields = ('role', 'groupe', 'periode', 'cours', 'classe', 'filiere', 'numero_telephone')
    filter_horizontal = ('cours',)


class FiltreGroupe(admin.SimpleListFilter):
    title = "Groupe"
    parameter_name = 'groupe'

    def lookups(self, request, model_admin):
        from scolarite.models import Groupe
        return [(g.id, g.nom) for g in Groupe.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(profil__groupe_id=self.value())
        return queryset


class FiltrePeriode(admin.SimpleListFilter):
    title = "Période"
    parameter_name = 'periode'

    def lookups(self, request, model_admin):
        from scolarite.models import Periode
        return [(p.id, p.nom) for p in Periode.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(profil__periode_id=self.value())
        return queryset


class FiltreClasse(admin.SimpleListFilter):
    title = "Classe"
    parameter_name = 'classe'

    def lookups(self, request, model_admin):
        from scolarite.models import Classe
        return [(c.id, c.nom) for c in Classe.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(profil__classe_id=self.value())
        return queryset


class FiltreFiliere(admin.SimpleListFilter):
    title = "Filière"
    parameter_name = 'filiere'

    def lookups(self, request, model_admin):
        from scolarite.models import Filiere
        return [(f.id, f.nom) for f in Filiere.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(profil__filiere_id=self.value())
        return queryset


class UtilisateurAdmin(UserAdmin):
    inlines = (ProfilInline,)
    list_display = (
        'username', 'first_name', 'last_name', 'email', 'is_staff',
        'role_affiche', 'groupe_affiche', 'periode_affiche',
        'classe_affichee', 'filiere_affichee',
    )
    list_filter = UserAdmin.list_filter + (FiltreGroupe, FiltrePeriode, FiltreClasse, FiltreFiliere)
    actions = ['exporter_excel', 'exporter_pdf']

    def get_inline_instances(self, request, obj=None):
        # Pas d'inline Profil sur la page d'AJOUT (le signal s'en charge deja) :
        # seulement sur la page de MODIFICATION, une fois le User cree.
        if not obj:
            return []
        return super().get_inline_instances(request, obj)

    def role_affiche(self, obj):
        return getattr(obj.profil, 'get_role_display', lambda: '-')()
    role_affiche.short_description = "Role"

    def groupe_affiche(self, obj):
        return obj.profil.groupe if hasattr(obj, 'profil') and obj.profil.groupe else "-"
    groupe_affiche.short_description = "Groupe"

    def periode_affiche(self, obj):
        return obj.profil.periode if hasattr(obj, 'profil') and obj.profil.periode else "-"
    periode_affiche.short_description = "Période"

    def classe_affichee(self, obj):
        return obj.profil.classe if hasattr(obj, 'profil') and obj.profil.classe else "-"
    classe_affichee.short_description = "Classe"

    def filiere_affichee(self, obj):
        return obj.profil.filiere if hasattr(obj, 'profil') and obj.profil.filiere else "-"
    filiere_affichee.short_description = "Filière"

    def exporter_excel(self, request, queryset):
        from rapports.exports import exporter_etudiants_excel
        return exporter_etudiants_excel(queryset)
    exporter_excel.short_description = "Exporter en Excel"

    def exporter_pdf(self, request, queryset):
        from rapports.exports import exporter_etudiants_pdf
        return exporter_etudiants_pdf(queryset)
    exporter_pdf.short_description = "Exporter en PDF"


# On reenregistre User avec l'inline Profil, pour creer un compte
# etudiant (identifiant + mot de passe) directement depuis /admin/.
admin.site.unregister(User)
admin.site.register(User, UtilisateurAdmin)
