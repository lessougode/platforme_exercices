from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Cours


@login_required
def liste_cours(request):
    if request.user.is_staff:
        cours = Cours.objects.filter(visible=True)
    else:
        profil = getattr(request.user, 'profil', None)
        if profil:
            cours = profil.cours.filter(visible=True)
        else:
            cours = Cours.objects.none()
    return render(request, 'cours/liste.html', {'cours': cours})
