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

- Un poste (celui qui sera le serveur) avec Python 3.10 ou plus récent,
  pour y installer PostgreSQL.
- L'exécutable de l'application déjà fabriqué (voir README, ou demander à
  la personne qui a suivi ce projet de le fournir directement — c'est plus
  simple que de refaire l'étape de fabrication sur place).
- Les noms des 5 personnes qui utiliseront l'application et le rôle de
  chacune (responsable / agent stock / agent comptabilité), et sur quel
  site (magasin de stock ou comptoir).
- Une imprimante ticket de caisse (thermique, en rouleau, 80mm) branchée
  sur le poste comptabilité — c'est là que le reçu final s'imprime. Si
  l'imprimante réelle fait 58mm plutôt que 80mm, il faut ajuster
  `LARGEUR_TICKET_MM` dans `modules/facturation.py`.

## Étape 1 — Préparer le poste serveur

1. Installer PostgreSQL sur ce poste (installateur officiel Windows/Mac).
2. Ouvrir une invite de commande dans le dossier du projet et exécuter :
   ```
   psql -U votre_utilisateur -d votre_base -f creation_base_donnees.sql
   ```
3. Noter l'adresse IP locale de ce poste (sur Windows : `ipconfig`, ligne
   « Adresse IPv4 » — ressemble à `192.168.1.xx`). **Cette adresse doit
   rester fixe** : dans les réglages du routeur, réserver cette adresse à
   ce poste (« réservation DHCP » ou « IP statique ») pour qu'elle ne
   change pas après un redémarrage — sinon les 4 autres postes perdront la
   connexion au serveur.
4. Copier `config.example.ini` vers `config.ini` (même dossier que
   l'exécutable) et renseigner :
   - `host` : l'adresse IP notée à l'étape 3
   - `user` / `password` : ceux créés à l'installation de PostgreSQL
5. Lancer `creer_compte_responsable.py` (ou demander à la personne qui a
   suivi ce projet de le faire à distance) pour créer le tout premier
   compte, celui du responsable.

## Étape 2 — Installer l'application sur les 5 postes

Sur **chacun des 5 postes**, y compris le serveur :

1. Copier deux fichiers dans un même dossier (par exemple sur le Bureau) :
   - `QuincaillerieFranck.exe` (l'exécutable)
   - `config.ini` — **le même sur les 5 postes**, avec l'adresse IP du
     poste serveur (celle notée à l'étape 1). C'est le seul fichier à
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
  toujours la bonne (voir étape 1.3 sur l'adresse fixe) ?
- **Compte verrouillé après plusieurs mauvais mots de passe** → le
  responsable peut le réactiver depuis l'onglet Utilisateurs.
- **Mot de passe oublié** → pas d'auto-réinitialisation pour l'instant ;
  le responsable désactive puis recrée le compte avec un nouveau mot de
  passe (onglet Utilisateurs), ou modifie l'identifiant existant en base
  si besoin d'aide technique.
- **Un poste n'affiche pas les derniers articles/ventes ajoutés ailleurs**
  → fermer et rouvrir l'onglet concerné (l'application ne se met pas à
  jour toute seule en continu, il faut rafraîchir).
