from django.urls import path

from . import views

urlpatterns = [
    path('', views.liste_exercices, name='liste_exercices'),
    path('historique/', views.historique, name='historique'),
    path('<int:exercice_id>/', views.detail_exercice, name='detail_exercice'),
    path('<int:exercice_id>/soumettre/', views.soumettre_exercice, name='soumettre_exercice'),
    path('tentative/<int:tentative_id>/revoir/', views.revoir_tentative, name='revoir_tentative'),
]