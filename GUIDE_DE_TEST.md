# Guide de test — scénario complet (Magasin, Comptoir, Responsable)

Ce guide vous fait rejouer une vraie journée de vente, avec des articles
concrets, pour vérifier que chaque poste se comporte normalement — y
compris les dernières nouveautés (verrouillage des prix, aperçu avant
impression, export Excel). Comptez environ 30 minutes.

Suivez les étapes **dans l'ordre** : chaque étape dépend souvent de la
précédente (ex : on ne peut pas encaisser une commande qui n'a pas encore
été enregistrée).

## Avant de commencer

1. Récupérez le code à jour (le zip que je vous ai envoyé, ou `git pull`
   si vous utilisez Git).
2. Si vous n'aviez pas encore exécuté `migration_v4_historique_prix.sql`
   sur votre base de test, faites-le maintenant :
   ```
   psql -U postgres -d quincaillerie_franck -f migration_v4_historique_prix.sql
   ```
3. Lancez l'application (`python main.py`, ou l'exécutable si vous l'avez
   déjà généré).

## Les personnages du test

| Personnage | Rôle | Poste | Identifiant à créer |
|---|---|---|---|
| Franck | Responsable | (déjà existant) | votre compte habituel |
| Amadou | Agent stock | Magasin de stock (matériaux lourds) | `a.magasin` |
| Chantal | Agent comptabilité | Comptoir | `c.comptoir` |

---

## Étape 1 — Connexion Responsable (Franck)

1. Connectez-vous avec votre compte responsable.
2. Onglet **Utilisateurs** → **+ Créer un compte** :
   - Nom complet : `Amadou Koffi` · Identifiant : `a.magasin` · Mot de
     passe : au choix (ex. `test1234`) · Rôle : **Agent stock** · Site :
     **Magasin de stock**.
   - Recommencez pour : `Chantal Mbarga` · Identifiant : `c.comptoir` ·
     Rôle : **Agent comptabilité** · Site : **Comptoir**.
3. Onglet **Articles** (nouveau : c'est vous qui gérez le catalogue des
   deux sites) — **+ Ajouter un article**, deux articles pour le
   Comptoir (Chantal en a besoin pour vendre à l'étape 3) :
   - Site **Comptoir** · Nom `Marteau` · Unité `unité` · Prix d'achat
     `2500` · Prix de vente `3500` · Quantité initiale `20` · Seuil `5`
   - Site **Comptoir** · Nom `Peinture blanche 1L` · Unité `litre` ·
     Prix d'achat `3200` · Prix de vente `4500` · Quantité initiale `15`
     · Seuil `3`
4. ✅ **À vérifier** : les deux comptes apparaissent dans la liste, les
   deux articles apparaissent avec la colonne **Site = Comptoir**.
5. Déconnectez-vous (fermez la fenêtre et relancez, ou le bouton de
   déconnexion si disponible).

---

## Étape 2 — Poste Magasin (Amadou), matériaux lourds

1. Connectez-vous avec `a.magasin`.
2. Onglet **Articles** — **+ Ajouter un article** (deux articles, sur
   *votre* site — pas de sélecteur de site, c'est normal, vous êtes déjà
   au Magasin de stock) :
   - Nom `Ciment CIM II 42,5 (sac)` · Catégorie `Matériaux` · Unité `sac`
     · Prix d'achat `4500` · Prix de vente `5500` · Quantité initiale
     `40` · Seuil `10`
   - Nom `Fer à béton 12mm (barre)` · Catégorie `Matériaux` · Unité
     `barre` · Prix d'achat `6000` · Prix de vente `7200` · Quantité
     initiale `8` · Seuil `10`
3. ✅ **À vérifier** : le fer à béton doit apparaître en **rouge/orangé**
   dans la colonne Stock (8 ≤ seuil 10) — c'est l'alerte de stock faible.
4. Cliquez **Modifier** sur « Ciment CIM II 42,5 » :
   - ✅ **À vérifier** : les champs **Prix d'achat** et **Prix de vente**
     doivent être **grisés, impossibles à modifier**. C'est volontaire
     (seul le responsable peut changer un prix déjà fixé). Changez juste
     la **Catégorie** en `Matériaux lourds` et enregistrez — ça, ça doit
     fonctionner.
5. Onglet **Tableau de bord** → **Mouvement stock** : Article `Fer à
   béton 12mm` · Type `Entrée` · Quantité `20` · Motif `Réception
   fournisseur`.
   - ✅ **À vérifier** : retournez sur Articles, le fer à béton est
     maintenant à 28 en stock, et n'est plus en alerte.
6. Onglet **Articles** → **Exporter Excel**, enregistrez le fichier sur
   le Bureau.
   - ✅ **À vérifier** : ouvrez le fichier avec Excel — vous devez voir
     les deux articles du magasin avec leurs quantités à jour.
7. Déconnectez-vous.

---

## Étape 3 — Poste Comptoir (Chantal), vente au comptant

1. Connectez-vous avec `c.comptoir`.
2. Onglet **Nouvelle commande** :
   - Recherchez et ajoutez `Marteau` (quantité 1) et `Peinture blanche
     1L` (quantité 2) au panier.
   - Vérifiez que le total TTC affiché semble cohérent (TVA 19,25%
     incluse).
   - Cliquez **Enregistrer — Facture détaillée** (pas « Ticket rapide »,
     pour tester la numérotation).
3. Une fenêtre doit s'ouvrir avec un seul bouton **Aperçu et
   impression** :
   - ✅ **À vérifier** : cliquez dessus — le PDF doit s'ouvrir dans
     votre lecteur habituel (Edge/Adobe), **pas** partir directement à
     l'imprimante. C'est le nouveau comportement demandé.
   - ✅ **À vérifier** : dans l'explorateur de fichiers
     (`Documents\Ventes_Quincaillerie`), le fichier doit s'appeler
     `Facture n° ... - AAAA-MM-JJ.pdf` (pas `facture_12.pdf`).
4. Enregistrez une deuxième commande, cette fois **Ticket rapide**, avec
   juste `Marteau` (quantité 1).
   - ✅ **À vérifier** : le fichier doit s'appeler `Ticket AAAA-MM-JJ
     14h32.pdf` (l'heure exacte variera, bien sûr).
5. Déconnectez-vous.

---

## Étape 4 — Retour Responsable (Franck), caisse et rapports

1. Reconnectez-vous avec votre compte responsable.
2. Onglet **Caisse** :
   - ✅ **À vérifier** : les deux commandes de Chantal apparaissent
     (« Enregistrée par Chantal Mbarga »).
   - Cliquez **Encaisser** sur la facture → mode de paiement
     **Espèces** → confirmez.
   - Cliquez **Encaisser** sur le ticket → mode de paiement **Orange
     Money** → confirmez.
   - ✅ **À vérifier** : la liste des commandes en attente est
     maintenant vide.
3. Essayez de recliquer *Encaisser* sur une commande déjà encaissée (si
   possible depuis l'écran) ou de l'annuler :
   - ✅ **À vérifier** : une commande déjà payée ne doit **jamais**
     pouvoir être annulée depuis cet écran (elle n'apparaît plus dans la
     liste, justement parce qu'elle est déjà traitée).
4. Onglet **Articles** → **Modifier** sur « Marteau » :
   - Changez le **Prix de vente** de `3500` à `3800` FCFA → Enregistrer.
   - Rouvrez **Modifier** sur le même article :
   - ✅ **À vérifier** : une ligne doit indiquer *« Dernier changement
     de prix par [votre nom] le [date] : vente 3500 → 3800 FCFA »*. C'est
     la traçabilité anti-vol.
5. Onglet **Rapports** :
   - ✅ **À vérifier** : le total des ventes doit inclure les deux
     commandes encaissées à l'étape 3 (Marteau ×1 + Peinture ×2 sur la
     facture, Marteau ×1 sur le ticket = 16 000 FCFA HT de marchandise,
     soit environ 19 080 FCFA TTC avec la TVA à 19,25%).
   - Cliquez **Exporter Excel**, enregistrez le fichier.
   - ✅ **À vérifier** : ouvrez-le — deux feuilles (« Résumé » et
     « Produits les plus vendus »), avec le Marteau qui apparaît vendu
     2 fois (1 sur la facture + 1 sur le ticket).

---

## Étape 5 — Cas limites (pour être vraiment rassuré)

Ces cas-là doivent **échouer proprement** (message d'erreur clair), pas
planter l'application :

1. **Stock insuffisant** : reconnectez-vous en `c.comptoir`, essayez de
   vendre 999 marteaux d'un coup → message d'erreur, aucune vente
   enregistrée.
2. **Cloisonnement par site** : reconnectez-vous en `a.magasin` et
   regardez la liste des articles.
   - ✅ **À vérifier** : le Marteau et la Peinture (articles du
     Comptoir) n'apparaissent **pas** dans la liste d'Amadou — chaque
     agent ne voit que les articles de son propre site ; seul le
     responsable voit et gère les deux sites.
3. **Compte désactivé** : en Franck, désactivez temporairement le compte
   `a.magasin`, puis essayez de vous connecter avec ce compte.
   - ✅ **À vérifier** : connexion refusée avec un message clair.
     Réactivez le compte ensuite pour ne pas bloquer Amadou.

---

## Si quelque chose ne va pas

Notez exactement : **quel poste** (Magasin/Comptoir/Responsable), **quel
écran**, **ce que vous avez cliqué**, et **le message ou comportement
inattendu** — avec si possible une capture d'écran. Renvoyez-moi ça et je
corrige.
