from django.contrib import admin

from .models import Groupe, Periode


@admin.register(Groupe)
class GroupeAdmin(admin.ModelAdmin):
    list_display = ('nom',)
    search_fields = ('nom',)


@admin.register(Periode)
class PeriodeAdmin(admin.ModelAdmin):
    list_display = ('nom', 'date_debut', 'date_fin', 'actif')
    list_filter = ('actif',)
