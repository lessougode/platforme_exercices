from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import Devoir, RenduDevoir


@login_required
def liste_devoirs(request):
    devoirs = Devoir.objects.filter(actif=True)
    rendus = {
        r.devoir_id: r
        for r in RenduDevoir.objects.filter(etudiant=request.user)
    }
    for d in devoirs:
        d.rendu_etudiant = rendus.get(d.id)
    return render(request, 'devoirs/liste.html', {'devoirs': devoirs})


@login_required
def envoyer_devoir(request, devoir_id):
    devoir = get_object_or_404(Devoir, id=devoir_id, actif=True)

    if request.method == 'POST':
        fichier = request.FILES.get('fichier')
        texte = request.POST.get('texte_reponse', '').strip()

        if not fichier and not texte:
            messages.error(request, "Envoie un fichier ou rédige une réponse avant de valider.")
            return render(request, 'devoirs/envoyer.html', {'devoir': devoir})

        defaults = {'commentaire_etudiant': request.POST.get('commentaire', ''), 'texte_reponse': texte}
        if fichier:
            defaults['fichier'] = fichier

        rendu, cree = RenduDevoir.objects.update_or_create(
            devoir=devoir, etudiant=request.user, defaults=defaults,
        )
        messages.success(request, "Ton travail a bien ete envoye.")
        return redirect('liste_devoirs')

    return render(request, 'devoirs/envoyer.html', {'devoir': devoir})
