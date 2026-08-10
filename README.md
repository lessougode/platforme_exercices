# Plateforme d'exercices

Application Django permettant :

- une connexion avec des identifiants créés uniquement par l'administrateur — pas d'auto-inscription ;
- un tableau de bord admin pour créer cours, exercices, questions et devoirs ;
- 3 types d'exercices (fixation, approfondissement, réflexion) et 4 types de questions
  (QCM unique/multiple, appariement, texte à trous, réponse libre notée manuellement),
  tous avec notation partielle façon Moodle, images de support, et coefficients ;
- une organisation scolaire complète : **Groupe**, **Classe** (primaire/secondaire),
  **Filière** (université), **Période** (trimestre ou semestre, avec année scolaire),
  et **Enseignant** (lié à ses cours et ses classes) ;
- un **Établissement** (nom, ville, quartier, téléphone, email, code/décision), affiché en
  en-tête des bulletins et résultats ;
- une page **Mon profil** pour chaque utilisateur : changer sa photo, son email et son
  numéro de téléphone, indépendamment les uns des autres ;
- des **exports Excel et PDF** :
  - liste des étudiants,
  - **bulletin** de groupe (notes /20, coefficients, moyenne pondérée /20 et /10, rang),
  - **résultats individuels** d'un étudiant (matières validées / non validées, points,
    moyennes, enseignant, période, année scolaire, établissement) ;
- des **notifications** par email (fonctionnel immédiatement), SMS et WhatsApp (via Twilio,
  à activer avec tes propres identifiants) ;
- un historique et suivi des travaux, avec revue détaillée des réponses ;
- un design travaillé, responsive (menu mobile), avec page d'accueil visiteur personnalisable.

## Démarrage rapide

```bash
python -m venv venv
source venv/bin/activate        # ou venv\Scripts\activate sous Windows
pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Organisation scolaire (à configurer dans `/admin/`)

| Modèle | Usage | Où |
|---|---|---|
| `ConfigurationSite` | Logo, image visiteur, titre du site | `/admin/scolarite/configurationsite/` (unique, non supprimable) |
| `Etablissement` | Nom, ville, quartier, téléphone, email, code/décision — affiché sur bulletins/résultats | `/admin/scolarite/etablissement/` (unique, non supprimable) |
| `Groupe` | Cohorte d'étudiants (ex: Groupe A) | `/admin/scolarite/groupe/` |
| `Classe` | Primaire / secondaire (ex: 6ème A, CM2) | `/admin/scolarite/classe/` |
| `Filiere` | Université (ex: Génie Informatique) | `/admin/scolarite/filiere/` |
| `Periode` | Trimestre ou semestre, avec année scolaire | `/admin/scolarite/periode/` |
| `Enseignant` | Nom, email, téléphone, ses cours et ses classes | `/admin/scolarite/enseignant/` |

Un étudiant (`Profil`, accessible depuis la fiche utilisateur `/admin/auth/user/<id>/change/`)
peut être relié à un `Groupe`, une `Periode`, une `Classe` **ou** une `Filiere` (selon son
niveau), et à un ou plusieurs `Cours` (case à cocher — voir section suivante).

`Cours`, `Exercice` et `Devoir` ont eux aussi des champs optionnels `periode`, `groupe`,
`classe`, `filiere` — utiles pour filtrer/organiser dans l'admin, mais **sans effet sur ce
qu'un étudiant voit** (voir ci-dessous).

## Comment un étudiant voit-il un cours ?

**Important** : un `Cours` marqué `visible` n'apparaît **pas automatiquement** à tous les
étudiants. Chaque étudiant ne voit que les cours qui lui ont été assignés individuellement :

1. Ouvre la fiche de l'étudiant dans `/admin/auth/user/<id>/change/`.
2. Dans la section "Profil", coche le ou les cours voulus dans **"Cours suivis"**.
3. Enregistre.

Le staff/admin, lui, voit tous les cours `visible=True` sans avoir besoin d'être assigné.

Si un cours "n'apparaît pas" côté étudiant après création : c'est très probablement qu'il
n'a pas encore été coché dans "Cours suivis" sur la fiche de cet étudiant.

## Page "Mon profil"

Chaque utilisateur connecté peut aller sur `/profil/` (lien "Paramètres" dans le menu) pour :

- ajouter ou changer sa **photo de profil** — si aucune photo n'est envoyée, l'avatar
  existant (ou l'avatar par défaut du site) reste inchangé ;
- ajouter ou changer son **email** ;
- ajouter ou changer son **numéro de téléphone**.

Chaque champ est indépendant : modifier l'email n'efface pas la photo, etc. Le changement de
photo se reflète immédiatement partout où l'avatar est affiché (menu latéral notamment).

## Utiliser les exports

Va dans le menu **Exports** (visible uniquement pour les comptes admin, `/gestion/`) :

1. **Liste des étudiants** : nom, prénom, identifiant, rôle, groupe, classe, filière, email,
   téléphone — filtrable par groupe.
2. **Bulletin** (par groupe) : choisis une période (obligatoire) et un groupe (optionnel) →
   génère un tableau avec chaque évaluation notée /20, la moyenne pondérée /20 et /10, le
   rang, l'établissement et le(s) enseignant(s) concerné(s) en en-tête.
3. **Résultats individuels** (par étudiant) : choisis un étudiant et une période →
   génère un document avec, par matière : enseignant(s), points obtenus/possibles,
   moyenne /20 et /10 — regroupés en **"Matières validées"** (moyenne ≥ 10/20) et
   **"Matières non validées"**, plus la moyenne générale. En-tête avec établissement,
   étudiant, période et année scolaire.

Le calcul ne prend en compte que les exercices terminés et les devoirs **corrigés**
(`corrige = coché` avec une `note` renseignée) de la période choisie. Une évaluation sans
note n'est pas comptée dans la moyenne d'un étudiant qui ne l'a pas faite.

Tu peux aussi exporter une sélection précise d'étudiants directement depuis
`/admin/auth/user/` : coche des utilisateurs puis choisis l'action "Exporter en Excel/PDF"
dans le menu déroulant en haut de la liste.

## Utiliser les notifications

Va dans `/admin/notifications/notification/add/` :
1. Écris l'objet et le message.
2. Choisis le canal (Email / SMS / WhatsApp).
3. Sélectionne des destinataires précis et/ou un groupe cible entier.
4. Enregistre en brouillon, puis coche-la dans la liste et choisis l'action
   **"Envoyer les notifications sélectionnées"**. Le rapport d'envoi (succès/échecs, et
   pourquoi) s'affiche ensuite dans la fiche de la notification.

**Email** fonctionne immédiatement : en développement, les emails s'affichent dans la
console (terminal où tourne `runserver`) au lieu d'être réellement envoyés. Pour un envoi
réel, complète le bloc SMTP dans `settings.py` (voir les commentaires, exemple avec Gmail).

**SMS et WhatsApp** nécessitent un compte [Twilio](https://www.twilio.com/try-twilio)
(gratuit pour démarrer/tester) :
1. Crée un compte, récupère `Account SID` et `Auth Token`.
2. Pour WhatsApp : active le "WhatsApp Sandbox" dans la console Twilio (gratuit en test).
3. Renseigne `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_SMS_FROM`,
   `TWILIO_WHATSAPP_FROM` dans `settings.py`.
4. Chaque étudiant doit avoir un `numero_telephone` renseigné (format international,
   ex: `+2250700000000`, modifiable depuis `/profil/`) pour recevoir un SMS/WhatsApp.

Tant que Twilio n'est pas configuré, l'envoi SMS/WhatsApp échoue proprement avec un message
d'erreur clair dans le rapport — le reste de l'application continue de fonctionner normalement.

## Créer rapidement un étudiant en ligne de commande

```bash
# Primaire / secondaire (classe)
python manage.py creer_etudiant kouassi.jean motdepasse123 --nom "Kouassi Jean" --classe "6eme A"

# Universite (filiere)
python manage.py creer_etudiant awa.kone motdepasse123 --nom "Awa Kone" --filiere "Genie Informatique"
```

## Multi-établissement

La plateforme est actuellement conçue pour **un seul établissement à la fois**
(`ConfigurationSite` et `Etablissement` sont des singletons : un seul enregistrement possible
pour chacun). Le support de plusieurs établissements sur une même installation n'est pas
encore implémenté — voir "Prochaines étapes suggérées" ci-dessous si ce besoin apparaît.

## Prochaines étapes suggérées

- Filtrer aussi le bulletin par matière (actuellement toutes les évaluations de la période
  sont mélangées).
- Ajouter un lien "Notifier" directement depuis la fiche d'un `Devoir` dans l'admin,
  pré-rempli.
- Historiser l'envoi (déclencher automatiquement une notification à la création d'un devoir).
- Multi-établissement : `Etablissement` en ForeignKey plutôt qu'en singleton, avec
  cloisonnement des données par établissement (voir discussion précédente si besoin).
