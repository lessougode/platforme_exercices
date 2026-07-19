from django.contrib import admin

from .models import Devoir, RenduDevoir


class RenduInline(admin.TabularInline):
    model = RenduDevoir
    extra = 0
    fields = ('etudiant', 'fichier', 'texte_reponse', 'note', 'corrige', 'date_soumission')
    readonly_fields = ('date_soumission',)


@admin.register(Devoir)
class DevoirAdmin(admin.ModelAdmin):
    list_display = ('titre', 'periode', 'coefficient', 'date_limite', 'actif', 'date_creation')
    list_filter = ('actif', 'periode')
    inlines = [RenduInline]


@admin.register(RenduDevoir)
class RenduDevoirAdmin(admin.ModelAdmin):
    list_display = ('etudiant', 'devoir', 'date_soumission', 'note', 'corrige')
    list_filter = ('devoir', 'corrige')
    search_fields = ('etudiant__username',)
