# Guide — envoyer l'application à des testeurs à distance

Ce guide est différent de `GUIDE_INSTALLATION.md` : celui-ci suppose 5
postes **sur le même réseau**, connectés à **une seule base de données
partagée**. Ici, chaque testeur est **ailleurs** (chez lui, une autre
ville) : il ne peut pas se connecter à votre base de données. Chaque
testeur va donc installer sa **propre base de données vide, séparée**, sur
son propre ordinateur — ses ventes de test n'apparaîtront jamais dans
votre vraie base, et inversement.

Le testeur n'a besoin d'installer que PostgreSQL — pas Python.

## Étape 1 — Vous : fabriquer les deux programmes (une seule fois)

Sur votre ordinateur (celui où `python main.py` fonctionne déjà) :

1. Double-cliquez sur `construire_exe.bat`.
2. Attendez qu'il termine (quelques minutes). Vous obtenez deux fichiers
   dans le dossier `dist` :
   - `QuincaillerieFranck.exe` — l'application elle-même
   - `CreerCompteResponsable.exe` — à lancer une seule fois par testeur,
     pour créer son premier compte (celui du responsable)

## Étape 2 — Vous : préparer le dossier à envoyer

Créez un dossier (par exemple `QuincaillerieFranck_Test`) et mettez-y :

- `dist\QuincaillerieFranck.exe`
- `dist\CreerCompteResponsable.exe`
- `creation_base_donnees.sql`
- `config.example.ini`
- `GUIDE_TESTEUR_INSTALLATION.txt` (voir contenu ci-dessous, à créer)

Puis compressez ce dossier en `.zip` et envoyez-le (WhatsApp, e-mail,
clé USB...) à chaque testeur.

**Ne mettez jamais `config.ini` (le vôtre) dans ce dossier** — chaque
testeur doit créer le sien avec ses propres identifiants PostgreSQL.

### Contenu à copier dans `GUIDE_TESTEUR_INSTALLATION.txt`

```
INSTALLATION — Ets Quincaillerie Franck (version de test)
============================================================

1. Installer PostgreSQL
   - Télécharger sur https://www.postgresql.org/download/windows/
   - Pendant l'installation, on vous demande un mot de passe pour
     l'utilisateur "postgres" : notez-le, vous en aurez besoin.
   - Laisser le port par défaut (5432).

2. Créer la base de données
   - Ouvrir "SQL Shell (psql)" (installé avec PostgreSQL, cherchez-le
     dans le menu Démarrer).
   - Appuyez sur Entrée à chaque question sauf pour le mot de passe
     (celui noté à l'étape 1).
   - Une fois connecté (invite "postgres=#"), tapez :
       CREATE DATABASE quincaillerie_test;
       \c quincaillerie_test
       \i 'CHEMIN_COMPLET_VERS\creation_base_donnees.sql'
     (remplacez CHEMIN_COMPLET_VERS par l'endroit où vous avez
     dézippé le dossier reçu, ex : C:\Users\VotreNom\Desktop\
     QuincaillerieFranck_Test\creation_base_donnees.sql)

3. Configurer l'application
   - Copier "config.example.ini", renommer la copie en "config.ini"
     (même dossier que QuincaillerieFranck.exe).
   - Ouvrir "config.ini" avec le Bloc-notes et renseigner :
       host = localhost
       port = 5432
       dbname = quincaillerie_test
       user = postgres
       password = (le mot de passe noté à l'étape 1)

4. Créer votre premier compte (responsable)
   - Double-cliquer sur "CreerCompteResponsable.exe".
   - Une fenêtre noire s'ouvre et pose 3 questions (nom, identifiant,
     mot de passe) : répondez et validez avec Entrée à chaque fois.
   - Une fois "Compte responsable créé avec succès" affiché, fermez
     la fenêtre.

5. Lancer l'application
   - Double-cliquer sur "QuincaillerieFranck.exe".
   - Se connecter avec l'identifiant et le mot de passe créés à
     l'étape 4.

Cette installation est totalement indépendante de la vraie base de la
quincaillerie : vous pouvez essayer, vous tromper, tout casser, sans
aucun risque sur les vraies données.
```

## Étape 3 — Ce qu'on demande au testeur

Une fois installé, demandez au testeur d'essayer les actions courantes :
créer un article, enregistrer une vente, consulter le tableau de bord,
faire un comptage d'inventaire (si compte agent stock créé aussi via
l'onglet Utilisateurs), etc.

Pour recueillir des retours utilisables, donnez-lui des questions
précises plutôt que "dis-moi ce que tu en penses" — par exemple :

- Qu'est-ce qui n'était pas clair ou pas facile à trouver ?
- Y a-t-il un écran où tu ne savais pas quoi faire ensuite ?
- Un message d'erreur bizarre ou peu clair est-il apparu ? (demander une
  capture d'écran si possible)
- Une fonctionnalité qui te manque, vue ton propre travail au quotidien ?
- Est-ce que les mots utilisés (français) sont clairs, ou y a-t-il des
  termes à changer ?

Le plus simple : demander les retours par écrit (WhatsApp, e-mail) pour
garder une trace, plutôt qu'à l'oral.
