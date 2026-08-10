from django.urls import path

from . import views

urlpatterns = [
    path('', views.liste_devoirs, name='liste_devoirs'),
    path('<int:devoir_id>/envoyer/', views.envoyer_devoir, name='envoyer_devoir'),
]
