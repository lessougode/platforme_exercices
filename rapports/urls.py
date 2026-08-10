from django.urls import path

from . import views

urlpatterns = [
    path('', views.formulaire, name='rapports_formulaire'),
    path('etudiants/<str:format_fichier>/', views.export_etudiants, name='export_etudiants'),
    path('bulletin/<str:format_fichier>/', views.export_bulletin, name='export_bulletin'),
    path('resultats/<str:format_fichier>/', views.export_resultats, name='export_resultats'),
]
