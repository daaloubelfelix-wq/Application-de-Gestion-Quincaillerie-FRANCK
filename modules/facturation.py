"""
Génération du reçu de vente en PDF, au format d'une imprimante ticket de
caisse (thermique, rouleau) — pas une imprimante de bureau A4/A5.

Circuit réel de la boutique (voir README, section « Circuit d'une
vente ») : le client paie d'abord directement à la caisse (le responsable
note à la main sur le facturier papier) ; la comptabilité saisit ensuite
la vente dans l'ordinateur EN UNE SEULE FOIS, puisque l'argent est déjà
reçu — c'est cette saisie qui génère et imprime directement le reçu
final (voir modules/ventes.py, enregistrer_vente). Il n'y a donc plus de
document intermédiaire avant paiement.

Le reçu imprime deux exemplaires à la suite sur le même rouleau (COPIE
CLIENT puis COPIE MAGASIN), comme un carnet à souche à papier carbone —
une seule impression suffit.

Largeur réglée pour une imprimante 80mm (la plus courante) ; si
l'imprimante réelle fait 58mm, changer LARGEUR_TICKET_MM ci-dessous.
"""

from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
from datetime import datetime

NOM_ETABLISSEMENT = "Ets Quincaillerie Franck"
ADRESSE_ETABLISSEMENT = "Batouri, Région de l'Est, Cameroun"
TELEPHONES_ETABLISSEMENT = "699 861217 / 654 226348"
TAUX_TVA = 19.25  # en pourcentage

LARGEUR_TICKET_MM = 80
LARGEUR_TICKET = LARGEUR_TICKET_MM * mm
MARGE_TICKET = 3 * mm
LARGEUR_UTILE = LARGEUR_TICKET - 2 * MARGE_TICKET

_POLICE_NORMALE = "Helvetica"
_POLICE_GRASSE = "Helvetica-Bold"
_POLICE_OBLIQUE = "Helvetica-Oblique"


def calculer_totaux(lignes_panier):
    """
    lignes_panier : liste de dicts {nom, quantite, prix_unitaire}
    Retourne (sous_total_ht, montant_tva, total_ttc)
    """
    sous_total_ht = sum(l["quantite"] * l["prix_unitaire"] for l in lignes_panier)
    montant_tva = round(sous_total_ht * TAUX_TVA / 100, 2)
    total_ttc = round(sous_total_ht + montant_tva, 2)
    return sous_total_ht, montant_tva, total_ttc


def _formater_montant(valeur):
    return f"{valeur:,.0f} FCFA".replace(",", " ")


def _decouper_texte(texte, police, taille, largeur_max):
    """Découpe texte en lignes qui tiennent dans largeur_max (rouleau très étroit)."""
    mots = texte.split()
    lignes = []
    ligne_actuelle = ""
    for mot in mots:
        essai = f"{ligne_actuelle} {mot}".strip()
        if stringWidth(essai, police, taille) <= largeur_max or not ligne_actuelle:
            ligne_actuelle = essai
        else:
            lignes.append(ligne_actuelle)
            ligne_actuelle = mot
    if ligne_actuelle:
        lignes.append(ligne_actuelle)
    return lignes


def _lignes_articles_decoupees(lignes_panier):
    """Pour chaque article, la ou les lignes de nom (si trop long) + la ligne de détail."""
    resultat = []
    for ligne in lignes_panier:
        lignes_nom = _decouper_texte(ligne["nom"], _POLICE_NORMALE, 9, LARGEUR_UTILE)
        detail = f"{ligne['quantite']} x {_formater_montant(ligne['prix_unitaire'])}"
        total_ligne = _formater_montant(ligne["quantite"] * ligne["prix_unitaire"])
        resultat.append((lignes_nom, detail, total_ligne))
    return resultat


def _hauteur_une_copie(lignes_articles_decoupees):
    """Hauteur en points nécessaire pour dessiner UNE copie du reçu."""
    hauteur = 0
    hauteur += 17.5 * mm          # nom + adresse + téléphone
    hauteur += 4 * (5 * mm)       # titre document, date/heure, vendeur, mode de paiement
    hauteur += 5 * mm             # ligne + espace avant articles
    for lignes_nom, _, _ in lignes_articles_decoupees:
        hauteur += len(lignes_nom) * 4.2 * mm
        hauteur += 7 * mm         # ligne de détail (qté x pu = total)
    hauteur += 5 * mm             # ligne + espace avant totaux
    hauteur += 5 * mm + 5.5 * mm + 8 * mm  # sous-total, tva, total
    hauteur += 6 * mm + 4 * mm    # remerciement + étiquette "COPIE ..."
    return hauteur


def _dessiner_une_copie(c, y_haut, etiquette_copie, type_document, numero_facture,
                         lignes_articles_decoupees, sous_total_ht, montant_tva, total_ttc,
                         nom_vendeur, mode_paiement_libelle, site_nom):
    """Dessine une copie complète du reçu, en partant de y_haut vers le bas.
    Retourne le y en bas de cette copie."""
    centre = LARGEUR_TICKET / 2
    y = y_haut

    c.setFont(_POLICE_GRASSE, 10)
    c.drawCentredString(centre, y, NOM_ETABLISSEMENT)
    y -= 5 * mm
    c.setFont(_POLICE_NORMALE, 7)
    c.drawCentredString(centre, y, f"{site_nom} · {ADRESSE_ETABLISSEMENT}")
    y -= 4.5 * mm
    c.drawCentredString(centre, y, f"Tél : {TELEPHONES_ETABLISSEMENT}")
    y -= 8 * mm

    c.setFont(_POLICE_GRASSE, 9)
    titre_document = f"FACTURE N° {numero_facture}" if type_document == "facture" else "TICKET DE CAISSE"
    c.drawCentredString(centre, y, titre_document)
    y -= 5 * mm
    c.setFont(_POLICE_NORMALE, 7)
    c.drawCentredString(centre, y, datetime.now().strftime("%d/%m/%Y %H:%M"))
    y -= 5 * mm
    c.drawCentredString(centre, y, f"Vendu par {nom_vendeur}")
    y -= 5 * mm
    c.drawCentredString(centre, y, f"Paiement : {mode_paiement_libelle}")
    y -= 6 * mm

    c.line(MARGE_TICKET, y, LARGEUR_TICKET - MARGE_TICKET, y)
    y -= 5 * mm

    for lignes_nom, detail, total_ligne in lignes_articles_decoupees:
        c.setFont(_POLICE_NORMALE, 9)
        for ligne_nom in lignes_nom:
            c.drawString(MARGE_TICKET, y, ligne_nom)
            y -= 4.2 * mm
        c.setFont(_POLICE_NORMALE, 8)
        c.drawString(MARGE_TICKET, y, detail)
        c.drawRightString(LARGEUR_TICKET - MARGE_TICKET, y, total_ligne)
        y -= 7 * mm

    c.line(MARGE_TICKET, y, LARGEUR_TICKET - MARGE_TICKET, y)
    y -= 5 * mm

    c.setFont(_POLICE_NORMALE, 8)
    c.drawString(MARGE_TICKET, y, "Sous-total HT")
    c.drawRightString(LARGEUR_TICKET - MARGE_TICKET, y, _formater_montant(sous_total_ht))
    y -= 5 * mm
    c.drawString(MARGE_TICKET, y, f"TVA ({TAUX_TVA}%)")
    c.drawRightString(LARGEUR_TICKET - MARGE_TICKET, y, _formater_montant(montant_tva))
    y -= 5.5 * mm

    c.setFont(_POLICE_GRASSE, 10)
    c.drawString(MARGE_TICKET, y, "TOTAL TTC")
    c.drawRightString(LARGEUR_TICKET - MARGE_TICKET, y, _formater_montant(total_ttc))
    y -= 8 * mm

    c.setFont(_POLICE_OBLIQUE, 7)
    c.drawCentredString(centre, y, "Merci de votre achat")
    y -= 6 * mm

    c.setFont(_POLICE_GRASSE, 8)
    c.drawCentredString(centre, y, f"— {etiquette_copie} —")
    y -= 4 * mm

    return y


def generer_recu_thermique_pdf(chemin_fichier, type_document, numero_facture, lignes_panier,
                                nom_vendeur, mode_paiement, site_nom):
    """
    Génère le reçu final (facture numérotée ou ticket) au format imprimante
    ticket, avec deux copies à la suite sur le même rouleau (COPIE CLIENT
    puis COPIE MAGASIN). Appelé uniquement quand l'argent a déjà été reçu
    (voir modules/ventes.py, enregistrer_vente).
    """
    from modules.paiement import libelle_mode_paiement

    sous_total_ht, montant_tva, total_ttc = calculer_totaux(lignes_panier)
    lignes_decoupees = _lignes_articles_decoupees(lignes_panier)
    mode_paiement_libelle = libelle_mode_paiement(mode_paiement)

    hauteur_copie = _hauteur_une_copie(lignes_decoupees)
    marge_haute_basse = 6 * mm
    hauteur_separateur = 10 * mm
    hauteur_page = marge_haute_basse * 2 + hauteur_copie * 2 + hauteur_separateur

    c = canvas.Canvas(chemin_fichier, pagesize=(LARGEUR_TICKET, hauteur_page))

    y = hauteur_page - marge_haute_basse
    for etiquette in ("COPIE CLIENT", "COPIE MAGASIN"):
        y = _dessiner_une_copie(
            c, y, etiquette, type_document, numero_facture, lignes_decoupees,
            sous_total_ht, montant_tva, total_ttc, nom_vendeur, mode_paiement_libelle, site_nom,
        )
        if etiquette == "COPIE CLIENT":
            y -= 4 * mm
            c.setDash(2, 2)
            c.line(MARGE_TICKET, y, LARGEUR_TICKET - MARGE_TICKET, y)
            c.setDash()
            c.setFont(_POLICE_NORMALE, 6)
            c.drawCentredString(LARGEUR_TICKET / 2, y - 3 * mm, "✂ - - - - - - - - - - - - - - - - -")
            y -= hauteur_separateur

    c.save()
    return sous_total_ht, montant_tva, total_ttc


# Clé arbitraire pour le verrou consultatif PostgreSQL qui sérialise
# l'attribution des numéros de facture (voir prochain_numero_facture).
_VERROU_NUMERO_FACTURE = 987654321


def prochain_numero_facture(cur):
    """
    Génère un numéro de facture séquentiel du type 2026-0001.

    Doit être appelé avec le curseur d'une transaction en cours
    (voir Database.transaction dans modules/ventes.py). Un verrou
    consultatif PostgreSQL empêche deux ventes simultanées d'obtenir
    le même numéro : la deuxième transaction attend que la première
    ait validé (ou annulé) avant de lire le dernier numéro.
    """
    cur.execute("SELECT pg_advisory_xact_lock(%s)", (_VERROU_NUMERO_FACTURE,))

    annee = datetime.now().year
    cur.execute(
        """
        SELECT numero_facture FROM ventes
        WHERE numero_facture LIKE %s
        ORDER BY id DESC LIMIT 1
        """,
        (f"{annee}-%",),
    )
    resultat = cur.fetchone()
    if resultat and resultat["numero_facture"]:
        dernier_numero = int(resultat["numero_facture"].split("-")[1])
        nouveau_numero = dernier_numero + 1
    else:
        nouveau_numero = 1
    return f"{annee}-{nouveau_numero:04d}"
