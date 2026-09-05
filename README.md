# Ets Quincaillerie Franck — Logiciel de gestion

Application de bureau (Windows/Mac) pour la gestion de la quincaillerie
à Batouri, région de l'Est, Cameroun.

> **Installation sur les 5 postes de la boutique ?** Suivre directement
> [`GUIDE_INSTALLATION.md`](GUIDE_INSTALLATION.md) — écrit pour un
> déploiement complet sans connaissances techniques. Le reste de ce
> README s'adresse plutôt à qui développe ou fabrique l'exécutable.

## Installation (poste de développement)

1. Installer Python 3.10 ou plus récent
2. Installer PostgreSQL sur le poste qui servira de serveur
3. Installer les dépendances Python :
   ```
   pip install -r requirements.txt
   ```

## Créer la base de données

Sur le serveur PostgreSQL, exécuter :
```
psql -U votre_utilisateur -d votre_base -f creation_base_donnees.sql
```

Puis copier `config.example.ini` vers `config.ini` (même dossier) et renseigner
l'adresse IP réelle du poste serveur ainsi que les identifiants de connexion.
`config.ini` contient un mot de passe : il ne doit jamais être partagé ni
envoyé sur GitHub (il est déjà exclu via `.gitignore`). Ce fichier doit être
recréé sur chaque poste (magasin, comptoir, bureau du responsable).

## Créer le premier compte (responsable)

Depuis le dossier du projet :
```
python creer_compte_responsable.py
```
Ce script demande le nom, l'identifiant et le mot de passe, puis crée
le compte avec un mot de passe correctement sécurisé (bcrypt).

Pour créer ensuite les comptes des agents (stock et comptabilité, sur
chacun des deux sites), se connecter avec le compte responsable et utiliser
l'onglet **Utilisateurs** dans l'application — pas besoin de requête SQL.

## Lancer l'application

```
python main.py
```

## Fabriquer l'exécutable à distribuer

Pour ne pas avoir à installer Python sur chacun des 5 postes de la
boutique, on fabrique une seule fois un exécutable autonome :

```
pip install -r requirements-empaquetage.txt
```
puis lancer `construire_exe.bat` (Windows) ou `./construire_exe.sh`
(Mac/Linux) depuis le dossier du projet. Le résultat apparaît dans
`dist/`. Voir [`GUIDE_INSTALLATION.md`](GUIDE_INSTALLATION.md) pour la
suite (copie sur les 5 postes, configuration, création des comptes).

## Structure du projet

```
quincaillerie_app/
├── GUIDE_INSTALLATION.md          Guide pas-à-pas pour installer sur les 5 postes
├── main.py                       Point d'entrée, navigation par onglets selon le rôle
├── database.py                   Connexion au serveur PostgreSQL + config.ini
├── config.example.ini            Modèle de configuration (à copier en config.ini)
├── creer_compte_responsable.py   Script à exécuter une seule fois
├── creation_base_donnees.sql     Script de création des tables
├── requirements.txt              Dépendances Python (usage normal)
├── requirements-empaquetage.txt  Dépendance supplémentaire pour fabriquer l'exécutable
├── construire_exe.bat            Fabrique l'exécutable Windows (voir plus haut)
├── construire_exe.sh             Fabrique l'exécutable Mac/Linux
├── modules/
│   ├── auth.py                   Authentification, verrouillage après 5 échecs
│   ├── articles.py                Gestion des articles et du stock
│   ├── ventes.py                  Enregistrement des ventes (transactionnel)
│   ├── facturation.py             Génération des PDF (ticket et facture)
│   ├── comptabilite.py            Recettes, dépenses, historique
│   ├── rapports.py                Totaux par période, produits les plus vendus
│   ├── fournisseurs.py            Gestion des fournisseurs
│   └── utilisateurs.py            Création et activation/désactivation des comptes
├── ui/
│   ├── login_window.py            Écran de connexion
│   ├── dashboard_agent.py         Tableau de bord agent (vue par site et par rôle)
│   ├── dashboard_responsable.py   Tableau de bord responsable (vue consolidée)
│   ├── gestion_articles.py        Liste, ajout, modification des articles
│   ├── formulaire_article.py      Formulaire article
│   ├── formulaire_mouvement_stock.py  Formulaire d'entrée/sortie de stock manuelle
│   ├── point_de_vente.py          Écran de vente (panier, ticket/facture)
│   ├── comptabilite.py            Écran comptabilité
│   ├── formulaire_transaction.py  Formulaire recette/dépense manuelle
│   ├── rapports.py                Écran rapports (responsable)
│   ├── gestion_fournisseurs.py    Liste et fiches fournisseurs
│   ├── formulaire_fournisseur.py  Formulaire fournisseur
│   ├── gestion_utilisateurs.py    Liste des comptes, activation/désactivation
│   └── formulaire_utilisateur.py  Formulaire de création de compte
└── api/                           Supervision mobile du responsable (lecture seule)
    ├── main.py                    Serveur FastAPI, sert aussi la page web mobile
    ├── routes.py                  Endpoints /api/connexion, /tableau-de-bord, /rapports…
    ├── securite.py                Jetons de session (JWT), réservés au rôle responsable
    └── static/index.html          Page web mobile (login + tableau de bord)
```

## Supervision mobile (responsable)

Le responsable peut consulter les recettes/dépenses du jour, les alertes de
stock et les rapports depuis son téléphone, où qu'il soit — via une page web
mobile (pas d'application à installer). Cette page est servie par un petit
serveur (`api/`) qui tourne sur le même poste que PostgreSQL et lit la même
base de données, en lecture seule.

### 1. Démarrer le serveur mobile

Sur le poste serveur (celui qui héberge déjà PostgreSQL), après avoir
installé les dépendances (`pip install -r requirements.txt`) et renseigné
la section `[api]` de `config.ini` (voir `config.example.ini` — une vraie
clé secrète, générée avec `python -c "import secrets; print(secrets.token_hex(32))"`) :

```
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

À ce stade, la page est déjà consultable depuis un téléphone connecté au
**même réseau Wi-Fi** que la boutique, à l'adresse `http://<IP du poste
serveur>:8000`. Pour un usage quotidien, il est préférable de lancer cette
commande comme service qui démarre automatiquement avec le PC (tâche
planifiée Windows, ou service `systemd` sous Linux) plutôt qu'à la main.

Seuls les comptes avec le rôle **responsable** peuvent se connecter à cette
page — un identifiant d'agent stock ou comptabilité est refusé, même avec
le bon mot de passe.

### 2. Rendre la page accessible depuis l'extérieur (Internet)

Pour que le responsable y accède aussi hors du réseau de la boutique, on
utilise un **tunnel Cloudflare** (`cloudflared`) : un petit programme
installé sur le poste serveur qui ouvre une connexion sortante chiffrée
vers Cloudflare et expose la page sur une adresse Internet stable, sans
toucher à la box Internet (pas d'ouverture de port) et sans coût.

1. Créer un compte Cloudflare gratuit et y ajouter un nom de domaine (un
   domaine peu coûteux suffit, ex. `quincaillerie-franck.com`) — nécessaire
   pour obtenir une adresse stable plutôt qu'une adresse temporaire.
2. Installer `cloudflared` sur le poste serveur (voir la documentation
   Cloudflare Tunnel pour Windows/Mac/Linux).
3. Créer le tunnel et le relier au serveur local :
   ```
   cloudflared tunnel login
   cloudflared tunnel create quincaillerie-franck
   cloudflared tunnel route dns quincaillerie-franck suivi.quincaillerie-franck.com
   cloudflared tunnel run --url http://localhost:8000 quincaillerie-franck
   ```
4. Le responsable ouvre alors `https://suivi.quincaillerie-franck.com`
   depuis son téléphone, où qu'il soit, et peut ajouter la page à son
   écran d'accueil comme un raccourci.

Comme pour le serveur mobile, `cloudflared tunnel run` doit rester actif en
permanence — à lancer comme service au démarrage du poste serveur.

*(Pour tester rapidement sans domaine, `cloudflared tunnel --url
http://localhost:8000` seul donne une adresse temporaire en
`trycloudflare.com`, valable tant que la commande tourne — pratique pour
un premier essai, mais l'adresse change à chaque redémarrage.)*

## Navigation par rôle

- **Agent stock** : Tableau de bord, Articles, Fournisseurs, Point de vente
- **Agent comptabilité** : Tableau de bord, Comptabilité, Point de vente
- **Responsable** : Tableau de bord (consolidé), Rapports, Fournisseurs, Utilisateurs

## Ce qui est fonctionnel

- Connexion avec identifiant/mot de passe, rôle et site détectés automatiquement,
  verrouillage après 5 tentatives échouées
- Tableau de bord agent (contenu différent pour stock et comptabilité) et
  responsable (vue consolidée avec sélecteur de site)
- Gestion des articles avec alertes de stock faible ; mouvement de stock manuel
  (entrée/sortie) accessible depuis le tableau de bord de l'agent stock
- Point de vente avec génération PDF au format ticket rapide OU facture
  détaillée numérotée, TVA à 19,25% incluse — enregistrement transactionnel
  (une vente est écrite intégralement ou pas du tout)
- Comptabilité : les ventes créent automatiquement une recette,
  saisie manuelle possible pour les dépenses
- Rapports : total des ventes, marge estimée, produits les plus vendus,
  filtrables par période et par site
- Fournisseurs : fiches avec liste des articles fournis
- Gestion des utilisateurs : création de compte, activation/désactivation
  (avec confirmation), déverrouillage automatique à la réactivation
- Supervision mobile : page web (login + tableau de bord + rapports)
  réservée au responsable, servie par `api/` — voir la section dédiée
  ci-dessus pour la rendre accessible depuis Internet

## Corrections apportées au code initial (voir l'audit)

- La vente est désormais enregistrée dans une seule transaction PostgreSQL,
  et la décrémentation du stock est atomique (protège contre la vente
  simultanée du dernier exemplaire d'un article sur deux postes)
- La numérotation des factures est protégée par un verrou (`pg_advisory_xact_lock`)
  contre les doublons en cas d'encaissement simultané
- Les identifiants de connexion à PostgreSQL sont sortis du code source vers
  `config.ini` (non versionné)
- Le changement de fournisseur d'un article est maintenant bien enregistré
  à la modification (il était silencieusement ignoré)
- Les boutons « Ajouter article » et « Mouvement stock » du tableau de bord
  agent sont maintenant fonctionnels

## Ce qu'il reste à développer

- Le responsable ne peut pas encore consulter/modifier les articles ou la
  comptabilité d'un site précis depuis l'application (seuls les rapports
  sont consolidés) — à ajouter si besoin
- Sauvegarde automatique quotidienne de la base de données (non codée,
  à mettre en place via une tâche planifiée `pg_dump` sur le serveur)
- Écran de consultation de l'historique des mouvements de stock
  (les données existent déjà en base, dans `mouvements_stock`)
- Mise en place effective du tunnel Cloudflare sur le poste serveur réel
  (domaine, `cloudflared` en service permanent) — la partie logicielle
  (API + page mobile) est prête, il reste l'installation sur place

