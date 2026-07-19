"""Calcul des bulletins : notes par evaluation, moyenne ponderee et rang."""
from decimal import Decimal

from django.contrib.auth.models import User

from comptes.models import Profil
from devoirs.models import Devoir, RenduDevoir
from exercices.models import Exercice, TentativeExercice


def calculer_bulletin(periode, groupe=None):
    """Renvoie (evaluations, lignes) pour une periode (et un groupe optionnel).

    evaluations : liste de dicts {label, coefficient, type}
    lignes : liste de dicts {etudiant, notes (liste de note/20 ou None), moyenne_20,
             moyenne_10, rang} triee par moyenne decroissante (ex-aequo geres).
    """
    etudiants_qs = User.objects.filter(profil__role=Profil.ETUDIANT).select_related('profil')
    if groupe:
        etudiants_qs = etudiants_qs.filter(profil__groupe=groupe)
    etudiants_qs = etudiants_qs.order_by('last_name', 'first_name', 'username')

    exercices = Exercice.objects.filter(periode=periode, actif=True).order_by('date_creation')
    devoirs = Devoir.objects.filter(periode=periode, actif=True).order_by('date_creation')

    evaluations = []
    for e in exercices:
        evaluations.append({'label': e.titre, 'coefficient': e.coefficient, 'type': 'exercice', 'objet': e})
    for d in devoirs:
        evaluations.append({'label': d.titre, 'coefficient': d.coefficient, 'type': 'devoir', 'objet': d})

    lignes = []
    for etudiant in etudiants_qs:
        notes = []
        total_pondere = Decimal('0')
        total_coef = Decimal('0')

        for ev in evaluations:
            note_20 = None
            if ev['type'] == 'exercice':
                tentative = TentativeExercice.objects.filter(
                    etudiant=etudiant, exercice=ev['objet'], termine=True
                ).first()
                if tentative and ev['objet'].total_points:
                    note_20 = (tentative.score_obtenu / ev['objet'].total_points) * Decimal('20')
            else:
                rendu = RenduDevoir.objects.filter(
                    etudiant=etudiant, devoir=ev['objet'], corrige=True, note__isnull=False
                ).first()
                if rendu:
                    note_20 = rendu.note

            notes.append(note_20)
            if note_20 is not None:
                total_pondere += note_20 * ev['coefficient']
                total_coef += ev['coefficient']

        moyenne_20 = (total_pondere / total_coef) if total_coef else None
        moyenne_10 = (moyenne_20 / 2) if moyenne_20 is not None else None

        lignes.append({
            'etudiant': etudiant,
            'notes': notes,
            'moyenne_20': moyenne_20.quantize(Decimal('0.01')) if moyenne_20 is not None else None,
            'moyenne_10': moyenne_10.quantize(Decimal('0.01')) if moyenne_10 is not None else None,
        })

    # Classement : memes moyennes = meme rang (ex-aequo), les etudiants sans
    # aucune note evaluee n'ont pas de rang et sont places en fin de liste.
    avec_moyenne = [l for l in lignes if l['moyenne_20'] is not None]
    sans_moyenne = [l for l in lignes if l['moyenne_20'] is None]
    avec_moyenne.sort(key=lambda l: l['moyenne_20'], reverse=True)

    rang_courant = 0
    moyenne_precedente = None
    for i, ligne in enumerate(avec_moyenne, start=1):
        if ligne['moyenne_20'] != moyenne_precedente:
            rang_courant = i
        ligne['rang'] = rang_courant
        moyenne_precedente = ligne['moyenne_20']
    for ligne in sans_moyenne:
        ligne['rang'] = None

    return evaluations, avec_moyenne + sans_moyenne
