import random
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Exercice, Question, ReponseEtudiant, TentativeExercice, arrondir


@login_required
def liste_exercices(request):
    exercices = Exercice.objects.filter(actif=True)
    tentatives = {
        t.exercice_id: t
        for t in TentativeExercice.objects.filter(etudiant=request.user, termine=True)
    }
    for e in exercices:
        e.tentative_etudiant = tentatives.get(e.id)
    return render(request, 'exercices/liste.html', {'exercices': exercices})


@login_required
def detail_exercice(request, exercice_id):
    exercice = get_object_or_404(Exercice, id=exercice_id, actif=True)
    questions = list(exercice.questions.prefetch_related('choix', 'paires', 'trous').all())

    # Pour l'appariement : construire la liste deroulante (options melangees) de chaque question.
    for q in questions:
        if q.type_question == Question.APPARIEMENT:
            options = [p.element_droite for p in q.paires.all()]
            random.shuffle(options)
            q.options_appariement = options

    return render(request, 'exercices/detail.html', {
        'exercice': exercice,
        'questions': questions,
    })


def _corriger_qcm(question, request):
    choix_coches = set(int(c) for c in request.POST.getlist(f'question_{question.id}'))
    donnees = {'choix': list(choix_coches)}

    tous_choix = list(question.choix.all())
    bons_ids = set(c.id for c in tous_choix if c.est_correct)
    mauvais_ids = set(c.id for c in tous_choix if not c.est_correct)

    if not bons_ids:
        return donnees, Decimal('0')

    if question.type_reponse_qcm == Question.UNIQUE:
        # Une seule bonne reponse attendue : tout ou rien.
        points = question.points if choix_coches == bons_ids else Decimal('0')
    else:
        # Plusieurs bonnes reponses possibles : notation partielle a la Moodle.
        # fraction = (coches corrects - coches incorrects) / nb corrects, bornee a [0, 1].
        nb_corrects_coches = len(choix_coches & bons_ids)
        nb_incorrects_coches = len(choix_coches & mauvais_ids)
        fraction = (nb_corrects_coches - nb_incorrects_coches) / len(bons_ids)
        fraction = max(Decimal('0'), min(Decimal('1'), Decimal(str(fraction))))
        points = arrondir(question.points * fraction)

    return donnees, points


def _corriger_appariement(question, request):
    paires = list(question.paires.all())
    if not paires:
        return {}, Decimal('0')

    reponses = {}
    nb_correctes = 0
    for paire in paires:
        valeur = request.POST.get(f'question_{question.id}_paire_{paire.id}', '').strip()
        reponses[str(paire.id)] = valeur
        if valeur.strip().lower() == paire.element_droite.strip().lower():
            nb_correctes += 1

    points_par_paire = question.points / len(paires)
    points = arrondir(points_par_paire * nb_correctes)
    return {'paires': reponses}, points


def _corriger_texte_trou(question, request):
    trous = list(question.trous.all())
    if not trous:
        return {}, Decimal('0')

    reponses = {}
    nb_correctes = 0
    for trou in trous:
        valeur = request.POST.get(f'question_{question.id}_trou_{trou.position}', '').strip()
        reponses[str(trou.position)] = valeur
        if trou.est_correct(valeur):
            nb_correctes += 1

    points_par_trou = question.points / len(trous)
    points = arrondir(points_par_trou * nb_correctes)
    return {'trous': reponses}, points


def _enregistrer_reponse_libre(question, request):
    """Question de type redaction : pas de correction automatique, l'admin notera
    manuellement depuis /admin/ (le score de la tentative se recalcule alors seul)."""
    texte = request.POST.get(f'question_{question.id}', '').strip()
    return {'texte': texte}, Decimal('0')


@login_required
def soumettre_exercice(request, exercice_id):
    """Corrige automatiquement la copie de l'etudiant, avec notation partielle
    pour les QCM a choix multiples, l'appariement et le texte a trous."""
    exercice = get_object_or_404(Exercice, id=exercice_id, actif=True)

    if request.method != 'POST':
        return redirect('detail_exercice', exercice_id=exercice.id)

    tentative, _ = TentativeExercice.objects.get_or_create(
        etudiant=request.user, exercice=exercice, defaults={}
    )
    tentative.reponses.all().delete()

    score_total = Decimal('0')
    for question in exercice.questions.all():
        if question.type_question == Question.QCM:
            donnees, points_obtenus = _corriger_qcm(question, request)
        elif question.type_question == Question.APPARIEMENT:
            donnees, points_obtenus = _corriger_appariement(question, request)
        elif question.type_question == Question.TEXTE_TROU:
            donnees, points_obtenus = _corriger_texte_trou(question, request)
        elif question.type_question == Question.REPONSE_LIBRE:
            donnees, points_obtenus = _enregistrer_reponse_libre(question, request)
        else:
            donnees, points_obtenus = {}, Decimal('0')

        ReponseEtudiant.objects.create(
            tentative=tentative, question=question,
            donnees_reponse=donnees, points_obtenus=points_obtenus,
        )
        score_total += points_obtenus

    tentative.score_obtenu = arrondir(score_total)
    tentative.termine = True
    tentative.date_soumission = timezone.now()
    tentative.save()

    return render(request, 'exercices/resultat.html', {
        'exercice': exercice,
        'tentative': tentative,
    })


@login_required
def historique(request):
    """Historique et suivi des travaux (exercices + devoirs) de l'etudiant connecte."""
    tentatives = TentativeExercice.objects.filter(
        etudiant=request.user, termine=True
    ).select_related('exercice').order_by('-date_soumission')

    from devoirs.models import RenduDevoir
    rendus = RenduDevoir.objects.filter(etudiant=request.user).select_related('devoir').order_by('-date_soumission')

    return render(request, 'exercices/historique.html', {
        'tentatives': tentatives,
        'rendus': rendus,
    })



@login_required
def revoir_tentative(request, tentative_id):
    """Permet a l'etudiant de revoir le detail de ses reponses (correctes/incorrectes) pour une tentative terminee."""
    tentative = get_object_or_404(
        TentativeExercice, id=tentative_id, etudiant=request.user, termine=True
    )
    reponses = {r.question_id: r for r in tentative.reponses.all()}

    details = []
    for q in tentative.exercice.questions.prefetch_related('choix', 'paires', 'trous').all():
        r = reponses.get(q.id)
        donnees = (r.donnees_reponse if r else {}) or {}
        item = {
            'question': q,
            'points_obtenus': r.points_obtenus if r else 0,
        }

        if q.type_question == Question.QCM:
            choix_coches = set(donnees.get('choix', []))
            item['choix'] = [
                {'choix': c, 'coche': c.id in choix_coches}
                for c in q.choix.all()
            ]

        elif q.type_question == Question.APPARIEMENT:
            paires_reponses = donnees.get('paires', {})
            item['paires'] = []
            for p in q.paires.all():
                reponse_donnee = paires_reponses.get(str(p.id), '')
                item['paires'].append({
                    'paire': p,
                    'reponse_donnee': reponse_donnee,
                    'correcte': reponse_donnee.strip().lower() == p.element_droite.strip().lower(),
                })

        elif q.type_question == Question.TEXTE_TROU:
            trous_reponses = donnees.get('trous', {})
            item['trous'] = []
            for t in q.trous.all():
                reponse_donnee = trous_reponses.get(str(t.position), '')
                item['trous'].append({
                    'trou': t,
                    'reponse_donnee': reponse_donnee,
                    'correcte': t.est_correct(reponse_donnee),
                })

        elif q.type_question == Question.REPONSE_LIBRE:
            item['texte_libre'] = donnees.get('texte', '')

        details.append(item)

    return render(request, 'exercices/revoir.html', {
        'tentative': tentative,
        'details': details,
    })
