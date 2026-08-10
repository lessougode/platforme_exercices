from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render

from comptes.models import Profil
from scolarite.models import Groupe, Periode

from . import exports
from .calculs import calculer_bulletin, calculer_resultats


@staff_member_required
def formulaire(request):
    return render(request, 'rapports/formulaire.html', {
        'periodes': Periode.objects.all(),
        'groupes': Groupe.objects.all(),
        'etudiants': User.objects.filter(profil__role=Profil.ETUDIANT).order_by('last_name', 'first_name'),
    })


@staff_member_required
def export_etudiants(request, format_fichier):
    queryset = User.objects.filter(profil__role=Profil.ETUDIANT)
    groupe_id = request.GET.get('groupe')
    if groupe_id:
        queryset = queryset.filter(profil__groupe_id=groupe_id)
    queryset = queryset.order_by('last_name', 'first_name')

    if format_fichier == 'excel':
        return exports.exporter_etudiants_excel(queryset)
    return exports.exporter_etudiants_pdf(queryset)


@staff_member_required
def export_bulletin(request, format_fichier):
    periode = get_object_or_404(Periode, id=request.GET.get('periode'))
    groupe = None
    if request.GET.get('groupe'):
        groupe = get_object_or_404(Groupe, id=request.GET.get('groupe'))

    evaluations, lignes = calculer_bulletin(periode, groupe)

    if format_fichier == 'excel':
        return exports.exporter_bulletin_excel(periode, groupe, evaluations, lignes)
    return exports.exporter_bulletin_pdf(periode, groupe, evaluations, lignes)


@staff_member_required
def export_resultats(request, format_fichier):
    periode = get_object_or_404(Periode, id=request.GET.get('periode'))
    etudiant = get_object_or_404(User, id=request.GET.get('etudiant'))

    resultats = calculer_resultats(etudiant, periode)

    if format_fichier == 'excel':
        return exports.exporter_resultats_excel(etudiant, periode, resultats)
    return exports.exporter_resultats_pdf(etudiant, periode, resultats)
