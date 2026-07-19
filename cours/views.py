from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Cours


@login_required
def liste_cours(request):
    cours = Cours.objects.filter(visible=True)
    return render(request, 'cours/liste.html', {'cours': cours})
