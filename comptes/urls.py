from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('connexion/', views.ConnexionView.as_view(), name='connexion'),
    path('deconnexion/', auth_views.LogoutView.as_view(), name='deconnexion'),
    path('', views.tableau_de_bord, name='tableau_de_bord'),
]
