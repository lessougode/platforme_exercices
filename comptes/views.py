from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render


class ConnexionView(auth_views.LoginView):
    template_name = 'comptes/connexion.html'


@login_required
def tableau_de_bord(request):
    """Point d'entree apres connexion : redirige vers l'admin Django si staff,
    sinon affiche le tableau de bord etudiant (cours, exercices, devoirs, historique)."""
    if request.user.is_staff:
        return redirect('/admin/')

    from exercices.models import TentativeExercice, Exercice
    from devoirs.models import Devoir
    from cours.models import Cours

    exercices_dispo = Exercice.objects.filter(actif=True)
    tentatives = TentativeExercice.objects.filter(etudiant=request.user, termine=True)
    exercices_faits_ids = tentatives.values_list('exercice_id', flat=True)

    contexte = {
        'cours_recents': Cours.objects.filter(visible=True)[:5],
        'devoirs_actifs': Devoir.objects.filter(actif=True)[:5],
        'exercices_a_faire': exercices_dispo.exclude(id__in=exercices_faits_ids)[:5],
        'derniers_resultats': tentatives.order_by('-date_soumission')[:5],
    }
    return render(request, 'comptes/tableau_de_bord.html', contexte)
