"""
Génération des documents de vente en PDF.

Circuit inspiré de la pharmacie : on ne remet jamais un document numéroté
avant que l'argent soit reçu. Trois documents possibles :
- bon de commande : remis par la comptabilité à l'enregistrement de la
  commande, AVANT paiement — non numéroté, explicitement marqué comme
  n'étant pas une facture (voir generer_bon_commande_pdf)
- ticket : remis à la caisse, APRÈS paiement — pas de numérotation
- facture : remise à la caisse, APRÈS paiement — numéro de facture
  séquentiel, attribué uniquement à l'encaissement (voir
  modules/ventes.py, encaisser_commande)
"""

from reportlab.lib.pagesizes import A5
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from datetime import datetime

NOM_ETABLISSEMENT = "Ets Quincaillerie Franck"
ADRESSE_ETABLISSEMENT = "Batouri, Région de l'Est, Cameroun"
TELEPHONES_ETABLISSEMENT = "699 861217 / 654 226348"
TAUX_TVA = 19.25  # en pourcentage


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


def generer_bon_commande_pdf(chemin_fichier, lignes_panier, nom_vendeur, site_nom):
    """
    Bon de commande remis au client par la comptabilité, AVANT paiement.
    Ce n'est volontairement PAS une facture ni un ticket : pas de
    numérotation, mention explicite que ce n'est pas un document fiscal.
    Le client le présente à la caisse pour payer et recevoir le document
    final (voir modules/ventes.py, encaisser_commande).
    """
    sous_total_ht, montant_tva, total_ttc = calculer_totaux(lignes_panier)

    c = canvas.Canvas(chemin_fichier, pagesize=A5)
    largeur, hauteur = A5
    marge = 15 * mm
    y = hauteur - marge

    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(largeur / 2, y, NOM_ETABLISSEMENT)
    y -= 6 * mm
    c.setFont("Helvetica", 8)
    c.drawCentredString(largeur / 2, y, f"{site_nom} · {ADRESSE_ETABLISSEMENT}")
    y -= 9 * mm

    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(largeur / 2, y, "BON DE COMMANDE")
    y -= 5 * mm
    c.setFont("Helvetica-Oblique", 7)
    c.drawCentredString(largeur / 2, y, "Ce document n'est pas une facture — à présenter à la caisse pour paiement")
    y -= 8 * mm

    c.setFont("Helvetica", 8)
    c.drawString(marge, y, f"{datetime.now().strftime('%d/%m/%Y %H:%M')} · Enregistré par {nom_vendeur}")
    y -= 8 * mm
    c.line(marge, y, largeur - marge, y)
    y -= 6 * mm

    c.setFont("Helvetica", 9)
    for ligne in lignes_panier:
        c.drawString(marge, y, ligne["nom"])
        y -= 5 * mm
        detail = f"{ligne['quantite']} x {_formater_montant(ligne['prix_unitaire'])}"
        total_ligne = _formater_montant(ligne["quantite"] * ligne["prix_unitaire"])
        c.setFont("Helvetica", 8)
        c.drawString(marge, y, detail)
        c.drawRightString(largeur - marge, y, total_ligne)
        c.setFont("Helvetica", 9)
        y -= 7 * mm

    c.line(marge, y, largeur - marge, y)
    y -= 8 * mm

    c.setFont("Helvetica-Bold", 13)
    c.drawString(marge, y, "À régler à la caisse")
    c.drawRightString(largeur - marge, y, _formater_montant(total_ttc))
    y -= 12 * mm

    c.setFont("Helvetica-Oblique", 8)
    c.drawCentredString(largeur / 2, y, "Merci de présenter ce bon à la caisse pour le paiement")

    c.save()
    return sous_total_ht, montant_tva, total_ttc


def generer_ticket_pdf(chemin_fichier, lignes_panier, nom_caissier, site_nom):
    """Génère un ticket de caisse compact, sans numérotation."""
    sous_total_ht, montant_tva, total_ttc = calculer_totaux(lignes_panier)

    c = canvas.Canvas(chemin_fichier, pagesize=A5)
    largeur, hauteur = A5
    marge = 15 * mm
    y = hauteur - marge

    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(largeur / 2, y, NOM_ETABLISSEMENT)
    y -= 6 * mm
    c.setFont("Helvetica", 8)
    c.drawCentredString(largeur / 2, y, f"{site_nom} · {ADRESSE_ETABLISSEMENT}")
    y -= 10 * mm

    c.setFont("Helvetica", 8)
    c.drawString(marge, y, f"{datetime.now().strftime('%d/%m/%Y %H:%M')} · Caisse {nom_caissier}")
    y -= 8 * mm
    c.line(marge, y, largeur - marge, y)
    y -= 6 * mm

    c.setFont("Helvetica", 9)
    for ligne in lignes_panier:
        c.drawString(marge, y, ligne["nom"])
        y -= 5 * mm
        detail = f"{ligne['quantite']} x {_formater_montant(ligne['prix_unitaire'])}"
        total_ligne = _formater_montant(ligne["quantite"] * ligne["prix_unitaire"])
        c.setFont("Helvetica", 8)
        c.drawString(marge, y, detail)
        c.drawRightString(largeur - marge, y, total_ligne)
        c.setFont("Helvetica", 9)
        y -= 7 * mm

    c.line(marge, y, largeur - marge, y)
    y -= 6 * mm

    c.setFont("Helvetica", 9)
    c.drawString(marge, y, "Sous-total HT")
    c.drawRightString(largeur - marge, y, _formater_montant(sous_total_ht))
    y -= 6 * mm
    c.drawString(marge, y, f"TVA {TAUX_TVA}%")
    c.drawRightString(largeur - marge, y, _formater_montant(montant_tva))
    y -= 6 * mm
    c.line(marge, y, largeur - marge, y)
    y -= 8 * mm

    c.setFont("Helvetica-Bold", 12)
    c.drawString(marge, y, "TOTAL TTC")
    c.drawRightString(largeur - marge, y, _formater_montant(total_ttc))
    y -= 12 * mm

    c.setFont("Helvetica-Oblique", 8)
    c.drawCentredString(largeur / 2, y, "Merci de votre achat")

    c.save()
    return sous_total_ht, montant_tva, total_ttc


def generer_facture_pdf(chemin_fichier, numero_facture, lignes_panier, nom_vendeur, site_nom):
    """Génère une facture détaillée avec en-tête, tableau et numérotation."""
    sous_total_ht, montant_tva, total_ttc = calculer_totaux(lignes_panier)

    c = canvas.Canvas(chemin_fichier, pagesize=A5)
    largeur, hauteur = A5
    marge = 15 * mm
    y = hauteur - marge

    # En-tête
    c.setFont("Helvetica-Bold", 13)
    c.drawString(marge, y, NOM_ETABLISSEMENT)
    c.setFont("Helvetica", 8)
    c.drawRightString(largeur - marge, y, f"Facture n° {numero_facture}")
    y -= 5 * mm
    c.drawString(marge, y, f"{site_nom} · {ADRESSE_ETABLISSEMENT}")
    c.drawRightString(largeur - marge, y, datetime.now().strftime("%d/%m/%Y"))
    y -= 5 * mm
    c.drawString(marge, y, f"Tél : {TELEPHONES_ETABLISSEMENT}")
    y -= 8 * mm
    c.line(marge, y, largeur - marge, y)
    y -= 8 * mm

    # En-tête du tableau
    c.setFont("Helvetica-Bold", 9)
    c.drawString(marge, y, "Article")
    c.drawString(marge + 70 * mm, y, "Qté")
    c.drawRightString(largeur - marge - 25 * mm, y, "P.U.")
    c.drawRightString(largeur - marge, y, "Total")
    y -= 3 * mm
    c.line(marge, y, largeur - marge, y)
    y -= 6 * mm

    c.setFont("Helvetica", 9)
    for ligne in lignes_panier:
        total_ligne = ligne["quantite"] * ligne["prix_unitaire"]
        c.drawString(marge, y, ligne["nom"])
        c.drawString(marge + 70 * mm, y, str(ligne["quantite"]))
        c.drawRightString(largeur - marge - 25 * mm, y, _formater_montant(ligne["prix_unitaire"]))
        c.drawRightString(largeur - marge, y, _formater_montant(total_ligne))
        y -= 6 * mm

    y -= 4 * mm
    c.line(marge, y, largeur - marge, y)
    y -= 8 * mm

    c.setFont("Helvetica", 9)
    c.drawString(largeur - marge - 60 * mm, y, "Sous-total HT")
    c.drawRightString(largeur - marge, y, _formater_montant(sous_total_ht))
    y -= 6 * mm
    c.drawString(largeur - marge - 60 * mm, y, f"TVA ({TAUX_TVA}%)")
    c.drawRightString(largeur - marge, y, _formater_montant(montant_tva))
    y -= 3 * mm
    c.line(largeur - marge - 60 * mm, y, largeur - marge, y)
    y -= 8 * mm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(largeur - marge - 60 * mm, y, "Total TTC")
    c.drawRightString(largeur - marge, y, _formater_montant(total_ttc))
    y -= 14 * mm

    c.setFont("Helvetica", 8)
    c.drawString(marge, y, f"Vendeur : {nom_vendeur} · Merci de votre confiance")

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
