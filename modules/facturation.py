"""
Génération des documents de vente en PDF.
Deux formats disponibles, comme validé lors de la conception :
- ticket : format compact A5, pas de numérotation
- facture : format détaillé A5, avec numéro de facture séquentiel
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
    return f"{valeur:,.0f} F".replace(",", " ")


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


def prochain_numero_facture():
    """Génère un numéro de facture séquentiel du type 2026-0001."""
    from database import Database
    annee = datetime.now().year
    resultat = Database.fetch_one(
        """
        SELECT numero_facture FROM ventes
        WHERE numero_facture LIKE %s
        ORDER BY id DESC LIMIT 1
        """,
        (f"{annee}-%",),
    )
    if resultat and resultat["numero_facture"]:
        dernier_numero = int(resultat["numero_facture"].split("-")[1])
        nouveau_numero = dernier_numero + 1
    else:
        nouveau_numero = 1
    return f"{annee}-{nouveau_numero:04d}"
