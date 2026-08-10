"""
Commande pratique pour creer rapidement un compte etudiant en ligne de commande :

    python manage.py creer_etudiant nom_utilisateur mot_de_passe --nom "Kouassi Jean" --classe "6eme A"
    python manage.py creer_etudiant nom_utilisateur mot_de_passe --nom "Kouassi Jean" --filiere "Genie Informatique"
"""
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from comptes.models import Profil


class Command(BaseCommand):
    help = "Cree un compte etudiant (identifiant + mot de passe)."

    def add_arguments(self, parser):
        parser.add_argument('username', type=str)
        parser.add_argument('password', type=str)
        parser.add_argument('--nom', type=str, default='', help="Nom complet")
        parser.add_argument('--classe', type=str, default='', help="Nom de la classe (primaire/secondaire)")
        parser.add_argument('--filiere', type=str, default='', help="Nom de la filiere (universite)")

    def handle(self, *args, **options):
        username = options['username']
        if User.objects.filter(username=username).exists():
            raise CommandError(f"L'utilisateur '{username}' existe deja.")

        prenom, _, nom = options['nom'].partition(' ')
        user = User.objects.create_user(
            username=username,
            password=options['password'],
            first_name=prenom,
            last_name=nom,
        )

        classe = None
        if options['classe']:
            from scolarite.models import Classe
            classe, _ = Classe.objects.get_or_create(nom=options['classe'])

        filiere = None
        if options['filiere']:
            from scolarite.models import Filiere
            filiere, _ = Filiere.objects.get_or_create(nom=options['filiere'])

        Profil.objects.filter(utilisateur=user).update(
            role=Profil.ETUDIANT, classe=classe, filiere=filiere
        )
        self.stdout.write(self.style.SUCCESS(
            f"Compte etudiant cree : {username} / {options['password']}"
        ))
