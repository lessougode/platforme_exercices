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


SEUIL_VALIDATION = Decimal('10')  # note /20 a partir de laquelle une matiere est consideree validee


def _enseignants_de_la_matiere(matiere):
    """Renvoie la liste des noms d'enseignants donnant au moins un cours
    rattache a cette matiere (via Enseignant.cours -> Cours.matiere)."""
    if matiere is None:
        return []
    from scolarite.models import Enseignant
    noms = Enseignant.objects.filter(cours__matiere=matiere).values_list('nom_complet', flat=True).distinct()
    return list(noms)


def calculer_resultats(etudiant, periode):
    """Renvoie les resultats d'un etudiant pour une periode, groupes par matiere.

    Renvoie un dict :
      {
        'matieres_validees': [ {matiere, enseignants, notes, total_points_obtenus,
                                 total_points_possibles, moyenne_20, moyenne_10}, ... ],
        'matieres_non_validees': [ ... meme structure ... ],
        'moyenne_generale_20': Decimal ou None,
        'moyenne_generale_10': Decimal ou None,
      }
    """
    exercices = Exercice.objects.filter(periode=periode, actif=True).select_related('matiere')
    devoirs = Devoir.objects.filter(periode=periode, actif=True).select_related('matiere')

    # Regroupement par matiere (cle = matiere ou None pour "Sans matiere")
    par_matiere = {}
    for e in exercices:
        par_matiere.setdefault(e.matiere, {'exercices': [], 'devoirs': []})['exercices'].append(e)
    for d in devoirs:
        par_matiere.setdefault(d.matiere, {'exercices': [], 'devoirs': []})['devoirs'].append(d)

    resultats_matieres = []
    total_pondere_general = Decimal('0')
    total_coef_general = Decimal('0')

    for matiere, contenu in par_matiere.items():
        total_pondere = Decimal('0')
        total_coef = Decimal('0')
        total_points_obtenus = Decimal('0')
        total_points_possibles = Decimal('0')
        notes = []

        for e in contenu['exercices']:
            tentative = TentativeExercice.objects.filter(etudiant=etudiant, exercice=e, termine=True).first()
            points_max = e.total_points or Decimal('0')
            points_obtenus = tentative.score_obtenu if tentative else Decimal('0')
            note_20 = (points_obtenus / points_max) * Decimal('20') if points_max else None

            notes.append({'label': e.titre, 'type': 'exercice', 'coefficient': e.coefficient, 'note_20': note_20})
            total_points_obtenus += points_obtenus
            total_points_possibles += points_max
            if note_20 is not None:
                total_pondere += note_20 * e.coefficient
                total_coef += e.coefficient

        for d in contenu['devoirs']:
            rendu = RenduDevoir.objects.filter(etudiant=etudiant, devoir=d, corrige=True, note__isnull=False).first()
            note_20 = rendu.note if rendu else None

            notes.append({'label': d.titre, 'type': 'devoir', 'coefficient': d.coefficient, 'note_20': note_20})
            total_points_possibles += Decimal('20')
            if note_20 is not None:
                total_points_obtenus += note_20
                total_pondere += note_20 * d.coefficient
                total_coef += d.coefficient

        moyenne_20 = (total_pondere / total_coef).quantize(Decimal('0.01')) if total_coef else None
        moyenne_10 = (moyenne_20 / 2).quantize(Decimal('0.01')) if moyenne_20 is not None else None

        if moyenne_20 is not None:
            total_pondere_general += moyenne_20 * total_coef
            total_coef_general += total_coef

        resultats_matieres.append({
            'matiere': matiere,
            'enseignants': _enseignants_de_la_matiere(matiere),
            'notes': notes,
            'total_points_obtenus': total_points_obtenus.quantize(Decimal('0.01')),
            'total_points_possibles': total_points_possibles.quantize(Decimal('0.01')),
            'moyenne_20': moyenne_20,
            'moyenne_10': moyenne_10,
            'validee': moyenne_20 is not None and moyenne_20 >= SEUIL_VALIDATION,
        })

    # Tri alphabetique par nom de matiere (les matieres sans nom en dernier)
    resultats_matieres.sort(key=lambda r: (r['matiere'] is None, str(r['matiere']) if r['matiere'] else ''))

    matieres_validees = [r for r in resultats_matieres if r['validee']]
    matieres_non_validees = [r for r in resultats_matieres if not r['validee']]

    moyenne_generale_20 = (total_pondere_general / total_coef_general).quantize(Decimal('0.01')) if total_coef_general else None
    moyenne_generale_10 = (moyenne_generale_20 / 2).quantize(Decimal('0.01')) if moyenne_generale_20 is not None else None

    return {
        'matieres_validees': matieres_validees,
        'matieres_non_validees': matieres_non_validees,
        'moyenne_generale_20': moyenne_generale_20,
        'moyenne_generale_10': moyenne_generale_10,
    }
