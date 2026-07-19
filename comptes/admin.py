from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Profil


class ProfilInline(admin.StackedInline):
    model = Profil
    can_delete = False
    verbose_name_plural = "Profil"
    fields = ('role', 'groupe', 'classe', 'numero_telephone')


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


class UtilisateurAdmin(UserAdmin):
    inlines = (ProfilInline,)
    list_display = ('username', 'first_name', 'last_name', 'email', 'is_staff', 'role_affiche', 'groupe_affiche')
    list_filter = UserAdmin.list_filter + (FiltreGroupe,)
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
