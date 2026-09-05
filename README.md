# Ets Quincaillerie Franck — Logiciel de gestion

Application de bureau (Windows/Mac) pour la gestion de la quincaillerie
à Batouri, région de l'Est, Cameroun.

## Installation

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

Pour créer ensuite les comptes des agents (stock et comptabilité,
sur chacun des deux sites), une requête SQL directe est nécessaire
pour l'instant — l'écran "Gestion des utilisateurs" permettant de le
faire depuis l'application est encore à développer.

## Lancer l'application

```
python main.py
```

## Structure du projet

```
quincaillerie_app/
├── main.py                       Point d'entrée, navigation par onglets selon le rôle
├── database.py                   Connexion au serveur PostgreSQL + config.ini
├── config.example.ini            Modèle de configuration (à copier en config.ini)
├── creer_compte_responsable.py   Script à exécuter une seule fois
├── creation_base_donnees.sql     Script de création des tables
├── requirements.txt              Dépendances Python
├── modules/
│   ├── auth.py                   Authentification, verrouillage après 5 échecs
│   ├── articles.py                Gestion des articles et du stock
│   ├── ventes.py                  Enregistrement des ventes (transactionnel)
│   ├── facturation.py             Génération des PDF (ticket et facture)
│   ├── comptabilite.py            Recettes, dépenses, historique
│   ├── rapports.py                Totaux par période, produits les plus vendus
│   ├── fournisseurs.py            Gestion des fournisseurs
│   └── utilisateurs.py            Création et activation/désactivation des comptes
└── ui/
    ├── login_window.py            Écran de connexion
    ├── dashboard_agent.py         Tableau de bord agent (vue par site et par rôle)
    ├── dashboard_responsable.py   Tableau de bord responsable (vue consolidée)
    ├── gestion_articles.py        Liste, ajout, modification des articles
    ├── formulaire_article.py      Formulaire article
    ├── formulaire_mouvement_stock.py  Formulaire d'entrée/sortie de stock manuelle
    ├── point_de_vente.py          Écran de vente (panier, ticket/facture)
    ├── comptabilite.py            Écran comptabilité
    ├── formulaire_transaction.py  Formulaire recette/dépense manuelle
    ├── rapports.py                Écran rapports (responsable)
    ├── gestion_fournisseurs.py    Liste et fiches fournisseurs
    ├── formulaire_fournisseur.py  Formulaire fournisseur
    ├── gestion_utilisateurs.py    Liste des comptes, activation/désactivation
    └── formulaire_utilisateur.py  Formulaire de création de compte
```

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
- Supervision mobile pour le responsable (application ou tableau de bord
  web à distance) — aucun code écrit pour l'instant, architecture à définir

