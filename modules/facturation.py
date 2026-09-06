"""
Génération du reçu de vente en PDF, au format d'une imprimante ticket de
caisse (thermique, rouleau) — pas une imprimante de bureau A4/A5. Mise en
page inspirée d'un ticket de caisse classique (police à chasse fixe,
séparateurs en tirets, montants alignés à points de suite, code-barres).

Circuit réel de la boutique (voir README, section « Circuit d'une
vente ») : le client paie d'abord directement à la caisse (le responsable
note à la main sur le facturier papier) ; la comptabilité saisit ensuite
la vente dans l'ordinateur EN UNE SEULE FOIS, puisque l'argent est déjà
reçu — c'est cette saisie qui génère et imprime directement le reçu
final (voir modules/ventes.py, enregistrer_vente). Il n'y a donc plus de
document intermédiaire avant paiement.

TVA à 0% : la marchandise est achetée déjà taxée auprès du fournisseur,
elle n'est pas taxée une seconde fois à la revente.

Le reçu imprime deux exemplaires à la suite sur le même rouleau (COPIE
CLIENT puis COPIE MAGASIN), comme un carnet à souche à papier carbone —
une seule impression suffit.

Largeur réglée pour une imprimante 80mm (la plus courante) ; si
l'imprimante réelle fait 58mm, changer LARGEUR_TICKET_MM ci-dessous.
"""

from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.graphics.barcode import code128
from datetime import datetime

NOM_ETABLISSEMENT = "Ets Quincaillerie Franck"
ADRESSE_ETABLISSEMENT = "Batouri, Région de l'Est, Cameroun"
TELEPHONES_ETABLISSEMENT = "699 861217 / 654 226348"
TAUX_TVA = 0  # en pourcentage — déjà taxé à l'achat auprès du fournisseur

LARGEUR_TICKET_MM = 80
LARGEUR_TICKET = LARGEUR_TICKET_MM * mm
MARGE_TICKET = 3 * mm
LARGEUR_UTILE = LARGEUR_TICKET - 2 * MARGE_TICKET

_POLICE_NORMALE = "Courier"
_POLICE_GRASSE = "Courier-Bold"
_COULEUR_TRAIT = colors.HexColor("#152C4D")


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
        lignes_nom = _decouper_texte(ligne["nom"].upper(), _POLICE_NORMALE, 8, LARGEUR_UTILE)
        detail = f"{ligne['quantite']} x {_formater_montant(ligne['prix_unitaire'])}"
        total_ligne = _formater_montant(ligne["quantite"] * ligne["prix_unitaire"])
        resultat.append((lignes_nom, detail, total_ligne))
    return resultat


def _ligne_pointillee(c, y, gauche, droite, police=_POLICE_NORMALE, taille=8):
    """Ex : "TOTAL . . . . . . . . 12 500 FCFA" — une seule chaîne, largeur exacte."""
    largeur_point = stringWidth(".", police, taille)
    largeur_fixe = stringWidth(f"{gauche} ", police, taille) + stringWidth(f" {droite}", police, taille)
    nb_points = max(3, int((LARGEUR_UTILE - largeur_fixe) / largeur_point))
    ligne = f"{gauche} {'.' * nb_points} {droite}"
    c.setFont(police, taille)
    c.drawString(MARGE_TICKET, y, ligne)


def _ligne_tiretee(c, y):
    c.setFont(_POLICE_NORMALE, 8)
    largeur_tiret = stringWidth("-", _POLICE_NORMALE, 8)
    nb_tirets = int(LARGEUR_UTILE / largeur_tiret)
    c.drawString(MARGE_TICKET, y, "-" * nb_tirets)


def _dessiner_logo(c, cx, cy, rayon):
    """Petit insigne dessiné (cercle + clé stylisée), pas de fichier image."""
    c.saveState()
    c.setStrokeColor(_COULEUR_TRAIT)
    c.setLineWidth(1.2)
    c.circle(cx, cy, rayon, stroke=1, fill=0)

    c.setLineWidth(2.4)
    c.setLineCap(1)
    dx, dy = rayon * 0.5, rayon * 0.5
    c.line(cx - dx, cy - dy, cx + dx, cy + dy)
    c.setFillColor(_COULEUR_TRAIT)
    c.circle(cx - dx, cy - dy, rayon * 0.24, stroke=0, fill=1)
    c.circle(cx + dx, cy + dy, rayon * 0.24, stroke=0, fill=1)
    c.restoreState()


def _hauteur_une_copie(lignes_articles_decoupees):
    """Hauteur en points nécessaire pour dessiner UNE copie du reçu."""
    hauteur = 0
    hauteur += 9 * mm             # logo
    hauteur += 5 * mm + 4.5 * mm  # nom établissement + site
    hauteur += 5 * mm             # ligne tiretée + espace
    hauteur += 4 * mm + 4 * mm    # adresse + téléphone
    hauteur += 5 * mm             # ligne tiretée + espace
    hauteur += 5 * mm             # titre document
    hauteur += 4 * mm             # date/heure
    hauteur += 4 * mm             # vente n° / vendeur
    hauteur += 5 * mm             # ligne tiretée + espace
    for lignes_nom, _, _ in lignes_articles_decoupees:
        hauteur += len(lignes_nom) * 3.8 * mm
        hauteur += 4.5 * mm       # ligne de détail (qté x pu = total)
    hauteur += 5 * mm             # ligne tiretée + espace
    hauteur += 4 * mm + 4 * mm    # sous-total, tva
    hauteur += 5 * mm             # ligne tiretée + espace
    hauteur += 5.5 * mm           # total
    hauteur += 5 * mm             # ligne tiretée + espace
    hauteur += 4.5 * mm           # mode de paiement
    hauteur += 7 * mm             # espace + merci
    hauteur += 3.8 * mm           # réclamation
    hauteur += 6 * mm             # espace + code-barres
    hauteur += 3.8 * mm           # texte sous le code-barres
    hauteur += 6 * mm             # étiquette "COPIE ..."
    return hauteur


def _dessiner_une_copie(c, y_haut, etiquette_copie, vente_id, type_document, numero_facture,
                         lignes_articles_decoupees, sous_total_ht, montant_tva, total_ttc,
                         nom_vendeur, mode_paiement_libelle, site_nom):
    """Dessine une copie complète du reçu, en partant de y_haut vers le bas.
    Retourne le y en bas de cette copie."""
    centre = LARGEUR_TICKET / 2
    y = y_haut

    _dessiner_logo(c, centre, y - 3 * mm, 3.6 * mm)
    y -= 9 * mm

    c.setFont(_POLICE_GRASSE, 10)
    c.drawCentredString(centre, y, NOM_ETABLISSEMENT.upper())
    y -= 5 * mm
    c.setFont(_POLICE_NORMALE, 8)
    c.drawCentredString(centre, y, site_nom.upper())
    y -= 4.5 * mm

    _ligne_tiretee(c, y)
    y -= 5 * mm

    c.setFont(_POLICE_NORMALE, 7)
    c.drawCentredString(centre, y, ADRESSE_ETABLISSEMENT)
    y -= 4 * mm
    c.drawCentredString(centre, y, f"TEL : {TELEPHONES_ETABLISSEMENT}")
    y -= 4 * mm

    _ligne_tiretee(c, y)
    y -= 5 * mm

    c.setFont(_POLICE_GRASSE, 10)
    titre_document = f"FACTURE N° {numero_facture}" if type_document == "facture" else "TICKET DE CAISSE"
    c.drawCentredString(centre, y, titre_document)
    y -= 5 * mm

    c.setFont(_POLICE_NORMALE, 7)
    maintenant = datetime.now()
    c.drawString(MARGE_TICKET, y, f"Date : {maintenant.strftime('%d/%m/%Y')}")
    c.drawRightString(LARGEUR_TICKET - MARGE_TICKET, y, maintenant.strftime("%H:%M"))
    y -= 4 * mm
    c.drawString(MARGE_TICKET, y, f"Vente N° {vente_id}")
    c.drawRightString(LARGEUR_TICKET - MARGE_TICKET, y, f"Vendu par {nom_vendeur}")
    y -= 5 * mm

    _ligne_tiretee(c, y)
    y -= 5 * mm

    for lignes_nom, detail, total_ligne in lignes_articles_decoupees:
        c.setFont(_POLICE_NORMALE, 8)
        for ligne_nom in lignes_nom:
            c.drawString(MARGE_TICKET, y, ligne_nom)
            y -= 3.8 * mm
        c.drawString(MARGE_TICKET, y, detail)
        c.drawRightString(LARGEUR_TICKET - MARGE_TICKET, y, total_ligne)
        y -= 4.5 * mm

    _ligne_tiretee(c, y)
    y -= 5 * mm

    _ligne_pointillee(c, y, "SOUS-TOTAL", _formater_montant(sous_total_ht))
    y -= 4 * mm
    _ligne_pointillee(c, y, f"TVA ({TAUX_TVA}%)", _formater_montant(montant_tva))
    y -= 4 * mm

    _ligne_tiretee(c, y)
    y -= 5.5 * mm

    _ligne_pointillee(c, y, "TOTAL", _formater_montant(total_ttc), police=_POLICE_GRASSE, taille=11)
    y -= 5 * mm

    _ligne_tiretee(c, y)
    y -= 4.5 * mm

    c.setFont(_POLICE_NORMALE, 8)
    c.drawCentredString(centre, y, f"MODE PAIEMENT : {mode_paiement_libelle.upper()}")
    y -= 7 * mm

    c.setFont(_POLICE_GRASSE, 10)
    c.drawCentredString(centre, y, "MERCI DE VOTRE ACHAT !")
    y -= 3.8 * mm
    c.setFont(_POLICE_NORMALE, 6.5)
    c.drawCentredString(centre, y, "Conservez ce reçu pour toute réclamation.")
    y -= 6 * mm

    code_barre_valeur = numero_facture if numero_facture else f"T{vente_id:06d}"
    code_barre = code128.Code128(code_barre_valeur, barHeight=6 * mm, barWidth=0.7)
    code_barre.drawOn(c, centre - code_barre.width / 2, y - 6 * mm)
    y -= 6 * mm
    c.setFont(_POLICE_NORMALE, 7)
    c.drawCentredString(centre, y - 3.8 * mm, f"*{code_barre_valeur}*")
    y -= 3.8 * mm

    y -= 6 * mm
    c.setFont(_POLICE_GRASSE, 8)
    c.drawCentredString(centre, y, f"— {etiquette_copie} —")
    y -= 4 * mm

    return y


def generer_recu_thermique_pdf(chemin_fichier, vente_id, type_document, numero_facture, lignes_panier,
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
            c, y, etiquette, vente_id, type_document, numero_facture, lignes_decoupees,
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
