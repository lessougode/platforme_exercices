from django.contrib.auth import views as auth_views
from django.shortcuts import redirect 
from django.urls import path

from . import views

urlpatterns = [
    path('', views.tableau_de_bord, name='tableau_de_bord'),
    path('connexion/', views.ConnexionView.as_view(), name='connexion'),
    path('deconnexion/', auth_views.LogoutView.as_view(), name='deconnexion'),
    path('profil/', views.modifier_profil, name='modifier_profil'),
    #path('', lambda request: redirect('/connexion/?next=/')),  # Modifiez cette ligne
]
