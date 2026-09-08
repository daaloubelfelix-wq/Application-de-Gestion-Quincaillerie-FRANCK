# Guide d'installation — 5 postes

Ce guide explique comment installer l'application sur les 5 postes de la
quincaillerie. Il est écrit pour être suivi sans connaissances
informatiques particulières. Prévoir environ une demi-journée pour la
première installation complète.

## Vue d'ensemble

```
                    ┌───────────────────────────┐
                    │   POSTE SERVEUR (1 seul)   │
                    │   PostgreSQL + la base     │
                    │   L'application (en plus)  │
                    └─────────────┬─────────────┘
                                  │ même réseau Wi-Fi / câblé
        ┌──────────┬──────────┬──┴───────┬──────────┐
        │          │          │          │          │
   ┌────┴───┐ ┌────┴───┐ ┌────┴───┐ ┌────┴───┐ ┌────┴───┐
   │ Poste 2│ │ Poste 3│ │ Poste 4│ │ Poste 5│ │ (mobile│
   │ agent  │ │ agent  │ │ agent  │ │ agent  │ │  du    │
   │        │ │        │ │        │ │        │ │respons.)│
   └────────┘ └────────┘ └────────┘ └────────┘ └────────┘
```

- **1 poste sert de serveur** : c'est lui qui garde toutes les données
  (ventes, stock, comptabilité). Il doit rester allumé et connecté au
  réseau pendant les heures d'ouverture — c'est le poste le plus important
  des 5. En général, on choisit le poste du bureau (le plus stable, le
  moins déplacé).
- **Les 5 postes ont tous l'application installée**, y compris le poste
  serveur. Chaque personne se connecte avec son propre identifiant et ne
  voit que ce que son rôle autorise (voir README, section « Navigation par
  rôle »).
- **Les 5 postes doivent être sur le même réseau** (même box/routeur
  Wi-Fi, ou câblés ensemble). L'application ne fonctionne pas si un poste
  est sur un réseau différent (ex : 4G du téléphone).

## Avant de commencer

- Sur place, il ne faut **pas** installer Python : les deux programmes
  nécessaires sont déjà fabriqués à l'avance (`QuincaillerieFranck.exe` et
  `CreerCompteResponsable.exe`, voir README ou demander à la personne qui a
  suivi ce projet de les fournir).
- Le poste choisi comme serveur (voir « Vue d'ensemble » ci-dessus) doit
  simplement avoir **PostgreSQL** installé dessus — rien d'autre de
  spécial. Ce n'est pas une machine à part : elle sert aussi normalement,
  comme les 4 autres, une fois tout installé.
- Les noms des 5 personnes qui utiliseront l'application et le rôle de
  chacune (responsable / agent stock / agent comptabilité), et sur quel
  site (magasin de stock ou comptoir).
- Une imprimante ticket de caisse (thermique, en rouleau, 80mm) branchée
  sur le poste comptabilité — c'est là que le reçu final s'imprime. Si
  l'imprimante réelle fait 58mm plutôt que 80mm, il faut ajuster
  `LARGEUR_TICKET_MM` dans `modules/facturation.py` (et refabriquer le
  `.exe`, avant de partir sur place).

## Étape 1 — Préparer le poste serveur

### 1.1 — Installer PostgreSQL

Installateur officiel Windows (`postgresql.org/download/windows`).
Pendant l'installation, un mot de passe est demandé pour l'utilisateur
`postgres` : **notez-le**, il sera réutilisé à chaque étape suivante.
Laisser le port par défaut (5432).

### 1.2 — Créer la base de données

Ouvrir « SQL Shell (psql) » (installé avec PostgreSQL, dans le menu
Démarrer). Entrée à chaque question sauf pour le mot de passe (celui
noté en 1.1). Une fois connecté (invite `postgres=#`) :
```
CREATE DATABASE quincaillerie_franck;
\c quincaillerie_franck
\i 'CHEMIN_COMPLET_VERS\creation_base_donnees.sql'
```
(remplacer `CHEMIN_COMPLET_VERS` par l'emplacement réel du fichier, par
exemple `C:\QuincaillerieFranck\creation_base_donnees.sql`)

### 1.3 — Noter l'adresse IP locale de ce poste, et la fixer

Invite de commande : `ipconfig`, ligne « Adresse IPv4 » — ressemble à
`192.168.1.xx`. **Cette adresse doit rester fixe** : dans les réglages du
routeur (box Internet), réserver cette adresse à ce poste (« réservation
DHCP » ou « IP statique », en utilisant son adresse physique — ligne
« Adresse physique » de `ipconfig /all`) pour qu'elle ne change pas après
un redémarrage — sinon les 4 autres postes perdront la connexion au
serveur. Si cette partie du routeur n'est pas claire, mieux vaut la faire
avec quelqu'un qui connaît les réglages de la box.

### 1.4 — Autoriser les connexions venant des 4 autres postes

Par défaut, PostgreSQL n'accepte que les connexions venant de
l'ordinateur lui-même. Sans cette étape, les 4 autres postes ne pourront
jamais se connecter, même avec la bonne adresse IP dans `config.ini`.

**a) Dans PostgreSQL** — dossier d'installation, sous-dossier `data`
(exemple : `C:\Program Files\PostgreSQL\18\data`) :

- Ouvrir `postgresql.conf` avec le Bloc-notes. Chercher la ligne
  `#listen_addresses = 'localhost'` et la remplacer par (sans le `#`) :
  ```
  listen_addresses = '*'
  ```
- Ouvrir `pg_hba.conf`. Ajouter tout en bas une ligne (adapter le début
  de l'adresse à celle notée en 1.3 — si elle commence par `192.168.1.`,
  garder tel quel) :
  ```
  host    all             all             192.168.1.0/24          scram-sha-256
  ```
- Enregistrer les deux fichiers, puis redémarrer le service : `Démarrer`
  → `services.msc` → Entrée → trouver `postgresql-x64-18` dans la liste →
  clic droit → **Redémarrer**.

**b) Dans le pare-feu Windows** — sinon Windows bloque quand même la
connexion, même si PostgreSQL l'accepterait :

- `Démarrer` → « Pare-feu Windows Defender avec fonctions avancées de
  sécurité » → Entrée.
- **Règles de trafic entrant** → **Nouvelle règle** → Type **Port** →
  Suivant.
- **TCP**, port spécifique `5432` → Suivant.
- **Autoriser la connexion** → Suivant → cocher les trois profils
  (Domaine, Privé, Public) → Suivant.
- Nom : `PostgreSQL Quincaillerie` → Terminer.

### 1.5 — Préparer `config.ini`

Copier `config.example.ini` vers `config.ini` (même dossier que
`QuincaillerieFranck.exe`) et renseigner :
```
host = 192.168.1.xx     ← l'adresse notée en 1.3 (jamais "localhost")
port = 5432
dbname = quincaillerie_franck
user = postgres
password = (le mot de passe noté en 1.1)
```
Ce même fichier sera copié tel quel sur les 4 autres postes à l'étape 2.

**Gardez une copie de ce fichier ailleurs qu'à cet endroit** (clé USB, ou
envoyé par e-mail/WhatsApp à vous-même) — s'il est effacé par erreur en
recopiant un dossier plus tard, il faudra sinon le retaper entièrement.

### 1.6 — Créer le compte responsable

Double-cliquer sur `CreerCompteResponsable.exe` (dans le même dossier que
`QuincaillerieFranck.exe`, avec `config.ini` déjà en place). Une fenêtre
noire pose 3 questions (nom complet, identifiant, mot de passe) —
répondre et valider avec Entrée à chaque fois. Une fois « Compte
responsable créé avec succès » affiché, fermer la fenêtre.

### 1.7 — Vérifier que le serveur fonctionne, avant d'aller plus loin

Lancer `QuincaillerieFranck.exe` **sur ce poste** et se connecter avec le
compte créé en 1.6. Si l'écran de connexion ne s'affiche pas ou qu'un
message « Impossible de joindre le serveur » apparaît, reprendre l'étape
1.4 avant de continuer — inutile d'installer les 4 autres postes tant que
le serveur lui-même n'est pas confirmé.

## Étape 2 — Installer l'application sur les 5 postes

Sur **chacun des 5 postes**, y compris le serveur :

1. Copier deux fichiers dans un même dossier (par exemple sur le Bureau) :
   - `QuincaillerieFranck.exe` (l'exécutable)
   - `config.ini` — **le même sur les 5 postes**, avec l'adresse IP du
     poste serveur (celle notée à l'étape 1.3). C'est le seul fichier à
     dupliquer partout.
2. Double-cliquer sur `QuincaillerieFranck.exe`. L'écran de connexion doit
   s'afficher.
3. Si un message « Impossible de joindre le serveur » apparaît : vérifier
   que le poste serveur est allumé, que les deux postes sont bien sur le
   même réseau, et que l'adresse IP dans `config.ini` est correcte.
4. Optionnel : créer un raccourci de `QuincaillerieFranck.exe` sur le
   Bureau pour un accès plus rapide.

## Étape 3 — Créer les comptes des 4 autres personnes

Une fois le compte responsable créé (étape 1) et l'application installée
quelque part :

1. Se connecter avec le compte responsable.
2. Ouvrir l'onglet **Utilisateurs**.
3. Cliquer sur **+ Créer un compte**, pour chacune des 4 personnes
   restantes : nom complet, identifiant (ex : `a.kone`), mot de passe
   initial, rôle (agent stock ou agent comptabilité), et site (magasin de
   stock ou comptoir).
4. Communiquer à chaque personne son identifiant et son mot de passe
   initial ; lui conseiller de le retenir (pas d'écran « mot de passe
   oublié » pour l'instant — voir « En cas de problème » ci-dessous).

Récapitulatif à remplir pendant l'installation :

| Poste | Personne | Identifiant | Rôle | Site |
|---|---|---|---|---|
| 1 (serveur) | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

## Étape 4 — Vérification finale

- [ ] Les 5 postes ouvrent l'application et affichent l'écran de connexion
- [ ] Chaque personne peut se connecter avec son propre identifiant
- [ ] Chacune voit bien les onglets correspondant à son rôle (voir README,
      section « Circuit d'une vente » et « Navigation par rôle »)
- [ ] Une vente test enregistrée par la comptabilité (avec un mode de
      paiement) diminue bien le stock (visible depuis un autre poste après
      actualisation) et le reçu final s'imprime directement
- [ ] Cette vente apparaît dans l'onglet **Historique des ventes** du
      responsable, avec le bon montant et le bon mode de paiement — les
      recettes du jour l'incluent immédiatement
- [ ] Le responsable voit les ventes des deux sites dans son tableau de bord

## Supervision mobile (optionnel)

Pour que le responsable consulte l'activité depuis son téléphone, y
compris hors de la boutique, voir le README, section « Supervision
mobile » — cette partie se configure une seule fois sur le poste serveur
et ne nécessite rien de plus sur les 4 autres postes.

## En cas de problème

- **« Impossible de joindre le serveur »** → le poste serveur est-il
  allumé et connecté au réseau ? L'adresse IP dans `config.ini` est-elle
  toujours la bonne (voir étape 1.3 sur l'adresse fixe) ? Cela fonctionne
  depuis le poste serveur lui-même mais pas depuis un autre poste →
  revoir l'étape 1.4 (pare-feu et `pg_hba.conf`), c'est presque toujours
  la cause.
- **Compte verrouillé après plusieurs mauvais mots de passe** → le
  responsable peut le réactiver depuis l'onglet Utilisateurs.
- **Mot de passe oublié** → pas d'auto-réinitialisation pour l'instant ;
  le responsable désactive puis recrée le compte avec un nouveau mot de
  passe (onglet Utilisateurs), ou modifie l'identifiant existant en base
  si besoin d'aide technique.
- **Un poste n'affiche pas les derniers articles/ventes ajoutés ailleurs**
  → fermer et rouvrir l'onglet concerné (l'application ne se met pas à
  jour toute seule en continu, il faut rafraîchir).
