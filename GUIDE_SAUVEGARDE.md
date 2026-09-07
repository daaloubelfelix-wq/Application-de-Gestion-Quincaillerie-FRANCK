# Guide de sauvegarde automatique

Ce guide explique comment mettre en place une sauvegarde automatique et
régulière de la base de données, pour pouvoir tout récupérer en cas de
panne, de vol ou de casse du poste serveur — sans dépendre de quelqu'un
qui doit se souvenir de le faire à la main.

## Pourquoi c'est important

Toutes les données de la boutique (ventes, stock, comptabilité, RH) sont
stockées **uniquement** sur le poste serveur. Sans sauvegarde, une panne
de disque dur, un vol, ou un incendie efface tout — définitivement. Le
volume de données reste petit (quelques Mo à quelques dizaines de Mo même
après des années) : ce n'est pas une question d'espace de stockage, mais
de régularité.

## Étape 1 — Enregistrer le mot de passe pour la sauvegarde automatique

Pour que la sauvegarde puisse se faire toute seule (sans qu'on tape le
mot de passe à chaque fois), PostgreSQL utilise un fichier spécial :

1. Ouvrir l'Explorateur de fichiers, coller dans la barre d'adresse :
   `%APPDATA%\postgresql` puis Entrée. Si le dossier `postgresql`
   n'existe pas, le créer (clic droit → Nouveau → Dossier, nommé
   `postgresql`), puis y retourner.
2. À l'intérieur, créer un fichier texte nommé exactement `pgpass.conf`
   (pas `pgpass.conf.txt` — dans l'Explorateur, activer l'affichage des
   extensions de fichiers si besoin pour vérifier : onglet Affichage →
   cocher « Extensions de noms de fichiers »).
3. Ouvrir ce fichier avec le Bloc-notes, et écrire une seule ligne :
   ```
   localhost:5432:quincaillerie_franck:postgres:VOTRE_MOT_DE_PASSE
   ```
   en remplaçant `VOTRE_MOT_DE_PASSE` par le vrai mot de passe
   PostgreSQL. Enregistrer.

**Ce fichier contient un mot de passe réel — comme `config.ini`, il ne
doit jamais être envoyé à personne ni mis sur GitHub.**

## Étape 2 — Tester la sauvegarde manuellement une fois

1. Vérifier dans `sauvegarder_base.bat` que `DBNAME` correspond bien au
   nom de votre base (`quincaillerie_franck` par défaut).
2. Double-cliquer sur `sauvegarder_base.bat`.
3. Une fenêtre s'ouvre et affiche soit `Sauvegarde reussie`, soit un
   message d'erreur. Si erreur, vérifier l'étape 1 (mot de passe) et
   que PostgreSQL est bien démarré.
4. Vérifier qu'un fichier `quincaillerie_AAAA-MM-JJ_HHMM.backup` est bien
   apparu dans `C:\Sauvegardes_Quincaillerie`.

## Étape 3 — Programmer la sauvegarde automatique (une fois pour toutes)

1. `Démarrer` → taper `Planificateur de tâches` → Entrée.
2. Colonne de droite → **Créer une tâche de base**.
3. Nom : `Sauvegarde Quincaillerie Franck` → Suivant.
4. Déclencheur : **Tous les jours**, à une heure après la fermeture
   (ex. 20h00) → Suivant.
5. Action : **Démarrer un programme** → Suivant.
6. Programme/script : cliquer **Parcourir**, sélectionner
   `sauvegarder_base.bat` → Suivant → **Terminer**.

À partir de maintenant, une sauvegarde se fait toute seule chaque soir,
même si personne n'y pense.

## Étape 4 — La sortir du magasin régulièrement

Une sauvegarde qui reste sur le même ordinateur ne protège pas contre un
vol ou un incendie qui touche tout le magasin en même temps. Deux
options, à faire de temps en temps (pas besoin que ce soit quotidien) :

- **Clé USB** : branchez-en une de temps en temps — le script copie
  automatiquement la dernière sauvegarde dessus si elle est présente
  (lettre `D:` par défaut ; si votre clé apparaît sous une autre lettre
  dans "Ce PC", ouvrir `sauvegarder_base.bat` avec le Bloc-notes et
  changer la ligne `DOSSIER_USB`).
- **Envoi à distance** (si une connexion Internet, même occasionnelle,
  est disponible) : envoyez-vous le fichier `.backup` le plus récent par
  e-mail ou WhatsApp de temps en temps, ou déposez-le sur un compte
  Google Drive.

## En cas de besoin : restaurer une sauvegarde

Si jamais il faut vraiment récupérer des données à partir d'une
sauvegarde :

1. Double-cliquer sur `restaurer_base.bat`.
2. Indiquer le chemin complet du fichier `.backup` à restaurer.
3. Cela crée une **nouvelle** base (`quincaillerie_franck_restauree`) —
   la base actuellement utilisée par l'application n'est jamais touchée
   automatiquement, pour éviter d'écraser des données par erreur.
4. Vérifiez le contenu de cette nouvelle base avant de l'utiliser
   réellement (au besoin, demandez de l'aide pour cette étape — mieux
   vaut vérifier avant de basculer dessus).
