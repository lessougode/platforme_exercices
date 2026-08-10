# Generated manually on 2026-08-06 (corrige la conversion classe : texte libre -> ForeignKey)

import django.db.models.deletion
from django.db import migrations, models


def migrer_classe_texte_vers_fk(apps, schema_editor):
    """Pour chaque ancienne valeur texte de profil.classe (non vide), cree
    (ou reutilise) l'objet Classe correspondant et relie le profil dessus."""
    Profil = apps.get_model('comptes', 'Profil')
    Classe = apps.get_model('scolarite', 'Classe')

    for profil in Profil.objects.exclude(classe_texte=''):
        nom = profil.classe_texte.strip()
        if not nom:
            continue
        classe, _ = Classe.objects.get_or_create(nom=nom)
        profil.classe_fk_id = classe.id
        profil.save(update_fields=['classe_fk'])


def revenir_en_arriere(apps, schema_editor):
    """Pas de reconstruction du texte libre au retour arriere : sans objet."""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('comptes', '0002_profil_cours_profil_periode'),
        ('scolarite', '0004_classe_filiere_periode_type_periode'),
    ]

    operations = [
        # 1) Nouveau champ filiere (rien a convertir, c'est un ajout simple).
        migrations.AddField(
            model_name='profil',
            name='filiere',
            field=models.ForeignKey(blank=True, help_text="Pour un étudiant d'université.", null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='etudiants', to='scolarite.filiere', verbose_name='Filière'),
        ),

        # 2) On renomme l'ancien champ texte pour le garder lisible pendant la conversion,
        #    et on cree un nouveau champ ForeignKey temporaire a cote.
        migrations.RenameField(
            model_name='profil',
            old_name='classe',
            new_name='classe_texte',
        ),
        migrations.AddField(
            model_name='profil',
            name='classe_fk',
            field=models.ForeignKey(blank=True, help_text='Pour un élève de primaire / secondaire.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='eleves', to='scolarite.classe', verbose_name='Classe'),
        ),

        # 3) Migration des donnees : cree les Classe manquantes et relie chaque profil.
        migrations.RunPython(migrer_classe_texte_vers_fk, reverse_code=revenir_en_arriere),

        # 4) Supprime l'ancien champ texte, puis renomme le nouveau champ a sa place.
        migrations.RemoveField(
            model_name='profil',
            name='classe_texte',
        ),
        migrations.RenameField(
            model_name='profil',
            old_name='classe_fk',
            new_name='classe',
        ),
    ]
