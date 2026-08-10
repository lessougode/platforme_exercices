from django.contrib import admin

from .models import Cours, Matiere


@admin.register(Matiere)
class MatiereAdmin(admin.ModelAdmin):
    list_display = ('nom',)


@admin.register(Cours)
class CoursAdmin(admin.ModelAdmin):
    list_display = ('titre', 'type_fichier', 'matiere', 'periode', 'groupe', 'classe', 'filiere', 'date_ajout', 'visible')
    list_filter = ('type_fichier', 'matiere', 'periode', 'groupe', 'classe', 'filiere', 'visible')
    search_fields = ('titre', 'description')
