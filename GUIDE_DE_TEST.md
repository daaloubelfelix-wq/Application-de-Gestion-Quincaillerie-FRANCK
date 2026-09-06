# Guide de test — scénario complet (Magasin, Comptoir, Responsable)

Ce guide vous fait rejouer une vraie journée de vente, avec des articles
concrets, pour vérifier que chaque poste se comporte normalement — y
compris les dernières nouveautés : circuit paiement-à-la-caisse-d'abord
(le client paie Franck directement, la comptabilité saisit ensuite tout
d'un coup), reçu façon ticket de caisse classique (police à chasse fixe,
code-barres, deux copies) avec TVA à 0%, verrouillage des prix, export
Excel. Comptez environ 30 minutes.

Suivez les étapes **dans l'ordre** : chaque étape dépend souvent de la
précédente (ex : on ne peut pas saisir dans l'historique une vente qui
n'a pas encore été enregistrée).

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

*Ce test n'utilise que 2 agents pour rester simple. En réalité, rien
n'empêche d'avoir 4 comptes distincts (un inventaire + une facturation
par site) : chaque compte ne voit et ne gère déjà que son propre site.*

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

## Étape 3 — Poste Comptoir (Chantal), saisie d'une vente déjà payée

Rappel du circuit réel : le client a **déjà payé** directement à Franck, à
la caisse, qui a noté la vente à la main sur le facturier papier. Chantal
saisit maintenant cette note dans l'ordinateur — en une seule fois,
puisque l'argent est déjà reçu.

1. Connectez-vous avec `c.comptoir`.
2. Onglet **Enregistrer une vente** :
   - Recherchez et ajoutez `Marteau` (quantité 1) et `Peinture blanche
     1L` (quantité 2) au panier.
   - Vérifiez que le total TTC affiché semble cohérent (TVA à 0% — la
     marchandise est déjà taxée à l'achat auprès du fournisseur).
   - Choisissez le mode de paiement `Espèces` (ce qui est indiqué sur le
     facturier).
   - Cliquez **Enregistrer — Facture détaillée** (pas « Ticket », pour
     tester la numérotation).
3. Une fenêtre doit s'ouvrir avec un seul bouton **Aperçu et
   impression** :
   - ✅ **À vérifier** : cliquez dessus — le PDF doit s'ouvrir dans
     votre lecteur habituel (Edge/Adobe), **pas** partir directement à
     l'imprimante.
   - ✅ **À vérifier** : le document s'appelle « FACTURE N° 2026-0001 »
     (numéro déjà attribué, puisque l'argent est déjà reçu), au format
     **étroit façon imprimante ticket** (pas une page A4/A5) — police à
     chasse fixe, séparateurs en tirets, un code-barres en bas — et
     contient le même contenu **deux fois à la suite** (« — COPIE CLIENT
     — » puis « — COPIE MAGASIN — », séparées par une ligne de coupe).
   - ✅ **À vérifier** : dans l'explorateur de fichiers
     (`Documents\Ventes_Quincaillerie`), le fichier doit s'appeler
     `Facture n° 2026-0001 - AAAA-MM-JJ.pdf`.
4. Enregistrez une deuxième vente, cette fois **Ticket**, avec juste
   `Marteau` (quantité 1) et mode de paiement `Orange Money`.
   - ✅ **À vérifier** : le fichier s'appelle `Ticket AAAA-MM-JJ
     14h32.pdf`, le document dit « TICKET DE CAISSE » (pas de numéro —
     les tickets n'en ont jamais).
5. Déconnectez-vous.

---

## Étape 4 — Retour Responsable (Franck), historique et rapports

1. Reconnectez-vous avec votre compte responsable.
2. Onglet **Historique des ventes** :
   - ✅ **À vérifier** : les deux ventes de Chantal apparaissent
     (« Enregistrée par Chantal Mbarga »), avec le bon numéro de facture
     pour la première, « Ticket » pour la seconde, et le mode de paiement
     de chacune (Espèces / Orange Money).
3. Cliquez **Annuler** sur le ticket, pour tester une correction d'erreur
   de saisie :
   - Une confirmation doit s'afficher avant toute action.
   - ✅ **À vérifier** : après confirmation, la ligne disparaît de
     l'historique. Retournez sur Articles (Comptoir) : le stock de
     Marteau doit avoir remonté de 1 (l'annulation restitue le stock).
4. Onglet **Articles** → **Modifier** sur « Marteau » :
   - Changez le **Prix de vente** de `3500` à `3800` FCFA → Enregistrer.
   - Rouvrez **Modifier** sur le même article :
   - ✅ **À vérifier** : une ligne doit indiquer *« Dernier changement
     de prix par [votre nom] le [date] : vente 3500 → 3800 FCFA »*. C'est
     la traçabilité anti-vol.
5. Onglet **Rapports** :
   - ✅ **À vérifier** : le total des ventes doit correspondre à la
     facture encore valide de l'étape 3 (Marteau ×1 + Peinture ×2 =
     12 500 FCFA — HT et TTC sont identiques, TVA à 0%) — le ticket
     annulé à l'étape précédente ne doit **plus** compter.
   - Cliquez **Exporter Excel**, enregistrez le fichier.
   - ✅ **À vérifier** : ouvrez-le — deux feuilles (« Résumé » et
     « Produits les plus vendus »).

---

## Étape 5 — Cas limites (pour être vraiment rassuré)

Ces cas-là doivent **échouer proprement** (message d'erreur clair), pas
planter l'application :

1. **Stock insuffisant** : reconnectez-vous en `c.comptoir`, essayez de
   vendre 999 marteaux d'un coup → message d'erreur, aucune vente
   enregistrée.
2. **Mode de paiement obligatoire** : essayez d'enregistrer une vente —
   le mode de paiement doit toujours avoir une valeur par défaut
   sélectionnée (jamais de champ vide qui bloquerait l'enregistrement).
3. **Cloisonnement par site** : reconnectez-vous en `a.magasin` et
   regardez la liste des articles.
   - ✅ **À vérifier** : le Marteau et la Peinture (articles du
     Comptoir) n'apparaissent **pas** dans la liste d'Amadou — chaque
     agent ne voit que les articles de son propre site ; seul le
     responsable voit et gère les deux sites. Notez aussi qu'Amadou n'a
     pas d'onglet « Enregistrer une vente » ni « Historique des ventes »
     — normal, ces deux écrans sont réservés à la comptabilité et au
     responsable.
4. **Compte désactivé** : en Franck, désactivez temporairement le compte
   `a.magasin`, puis essayez de vous connecter avec ce compte.
   - ✅ **À vérifier** : connexion refusée avec un message clair.
     Réactivez le compte ensuite pour ne pas bloquer Amadou.

---

## Si quelque chose ne va pas

Notez exactement : **quel poste** (Magasin/Comptoir/Responsable), **quel
écran**, **ce que vous avez cliqué**, et **le message ou comportement
inattendu** — avec si possible une capture d'écran. Renvoyez-moi ça et je
corrige.
