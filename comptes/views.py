from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import ModifierProfilForm
from .models import Profil


class ConnexionView(auth_views.LoginView):
    template_name = 'comptes/connexion.html'


def tableau_de_bord(request):
    """Page racine du site ('/').

    - Visiteur non connecté : page d'accueil (logo + image "visiteur" définis
      dans l'admin via ConfigurationSite).
    - Utilisateur staff connecté : redirection vers l'admin Django.
    - Étudiant connecté : tableau de bord (cours, exercices, devoirs, historique).
    """
    if not request.user.is_authenticated:
        return render(request, 'comptes/accueil.html')

    if request.user.is_staff:
        return redirect('/admin/')

    from exercices.models import TentativeExercice, Exercice
    from devoirs.models import Devoir
    from cours.models import Cours

    profil = getattr(request.user, 'profil', None)
    cours_recents = profil.cours.filter(visible=True)[:5] if profil else Cours.objects.none()

    exercices_dispo = Exercice.objects.filter(actif=True)
    tentatives = TentativeExercice.objects.filter(etudiant=request.user, termine=True)
    exercices_faits_ids = tentatives.values_list('exercice_id', flat=True)

    contexte = {
        'cours_recents': cours_recents,
        'devoirs_actifs': Devoir.objects.filter(actif=True)[:5],
        'exercices_a_faire': exercices_dispo.exclude(id__in=exercices_faits_ids)[:5],
        'derniers_resultats': tentatives.order_by('-date_soumission')[:5],
    }
    return render(request, 'comptes/tableau_de_bord.html', contexte)


@login_required
def modifier_profil(request):
    """Page 'Paramètres' : l'utilisateur connecté modifie sa photo, son email
    et son numéro de téléphone. Chaque champ est optionnel et indépendant :
    ne pas envoyer de nouvelle photo laisse l'avatar existant inchangé."""
    profil, _ = Profil.objects.get_or_create(utilisateur=request.user)

    if request.method == 'POST':
        form = ModifierProfilForm(request.POST, request.FILES, instance=profil, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil mis à jour avec succès.")
            return redirect('modifier_profil')
    else:
        form = ModifierProfilForm(instance=profil, user=request.user)

    return render(request, 'comptes/profil.html', {'form': form, 'profil': profil})
