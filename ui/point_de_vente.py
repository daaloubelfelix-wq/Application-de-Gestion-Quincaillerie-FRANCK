"""
Écran d'enregistrement des commandes clients (tenu par la comptabilité).
Recherche d'articles (limitée au catalogue du site de l'utilisateur),
panier, calcul automatique de la TVA, et choix entre ticket rapide
ou facture détaillée.

Cet écran ne prend PAS le paiement : il enregistre la commande (le stock
est retiré immédiatement) et imprime le montant à payer. Le client va
ensuite payer à la caisse (voir ui/caisse.py, tenu par le responsable).
"""

import os
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QMessageBox, QFileDialog, QFrame
)
from PyQt6.QtCore import Qt

from modules.ventes import enregistrer_commande, rechercher_articles
from modules.facturation import calculer_totaux, generer_ticket_pdf, generer_facture_pdf
from ui.dialogue_document import DialogueDocumentGenere


class PointDeVente(QWidget):
    def __init__(self, utilisateur):
        super().__init__()
        self.utilisateur = utilisateur
        self.panier = []  # liste de dicts {article_id, nom, quantite, prix_unitaire, stock_disponible}
        self._construire_interface()

    # ------------------------------------------------------------
    # Construction de l'interface
    # ------------------------------------------------------------
    def _construire_interface(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        titre = QLabel(f"Nouvelle commande · {self.utilisateur['site_nom']}")
        titre.setObjectName("titreEcran")
        layout.addWidget(titre)

        sous_titre = QLabel("Le client paiera à la caisse une fois la commande enregistrée.")
        sous_titre.setObjectName("texteAttenue")
        layout.addWidget(sous_titre)

        # Barre de recherche
        self.champ_recherche = QLineEdit()
        self.champ_recherche.setPlaceholderText("Rechercher un article...")
        self.champ_recherche.textChanged.connect(self._rechercher)
        layout.addWidget(self.champ_recherche)

        # Résultats de recherche
        self.liste_resultats = QListWidget()
        self.liste_resultats.setMaximumHeight(120)
        self.liste_resultats.itemDoubleClicked.connect(self._ajouter_au_panier)
        layout.addWidget(self.liste_resultats)

        # Panier
        titre_panier = QLabel("Panier")
        titre_panier.setObjectName("titreSection")
        layout.addWidget(titre_panier)

        self.liste_panier = QListWidget()
        layout.addWidget(self.liste_panier)

        bouton_retirer = QPushButton("Retirer l'article sélectionné")
        bouton_retirer.setProperty("secondaire", True)
        bouton_retirer.clicked.connect(self._retirer_du_panier)
        layout.addWidget(bouton_retirer)

        # Récapitulatif des totaux
        self.cadre_totaux = QFrame()
        self.cadre_totaux.setObjectName("carteTotaux")
        self._construire_zone_totaux()
        layout.addWidget(self.cadre_totaux)

        # Boutons d'enregistrement de la commande
        actions = QHBoxLayout()
        bouton_ticket = QPushButton("Enregistrer — Ticket rapide")
        bouton_ticket.clicked.connect(lambda: self._enregistrer_commande("ticket"))
        bouton_facture = QPushButton("Enregistrer — Facture détaillée")
        bouton_facture.clicked.connect(lambda: self._enregistrer_commande("facture"))
        actions.addWidget(bouton_ticket)
        actions.addWidget(bouton_facture)
        layout.addLayout(actions)

        self.setLayout(layout)

    def _construire_zone_totaux(self):
        vlayout = QVBoxLayout()
        self.label_sous_total = QLabel("Sous-total HT : 0 FCFA")
        self.label_tva = QLabel("TVA (19,25%) : 0 FCFA")
        self.label_total = QLabel("Total à payer à la caisse : 0 FCFA")
        self.label_total.setObjectName("totalMisEnValeur")
        vlayout.addWidget(self.label_sous_total)
        vlayout.addWidget(self.label_tva)
        vlayout.addWidget(self.label_total)
        self.cadre_totaux.setLayout(vlayout)

    # ------------------------------------------------------------
    # Recherche et gestion du panier
    # ------------------------------------------------------------
    def _rechercher(self, texte):
        self.liste_resultats.clear()
        if len(texte.strip()) < 2:
            return
        for article in rechercher_articles(self.utilisateur["site_id"], texte.strip()):
            libelle = f"{article['nom']} — {article['prix_vente']:.0f} FCFA ({article['quantite_stock']} en stock)"
            item = QListWidgetItem(libelle)
            item.setData(Qt.ItemDataRole.UserRole, article)
            self.liste_resultats.addItem(item)

    def _ajouter_au_panier(self, item):
        article = item.data(Qt.ItemDataRole.UserRole)

        if article["quantite_stock"] <= 0:
            QMessageBox.warning(self, "Rupture de stock", f"'{article['nom']}' n'est plus en stock.")
            return

        # Si déjà dans le panier, on augmente juste la quantité
        for ligne in self.panier:
            if ligne["article_id"] == article["id"]:
                if ligne["quantite"] + 1 > article["quantite_stock"]:
                    QMessageBox.warning(self, "Stock insuffisant", f"Stock disponible : {article['quantite_stock']}.")
                    return
                ligne["quantite"] += 1
                self._rafraichir_panier()
                return

        self.panier.append({
            "article_id": article["id"],
            "nom": article["nom"],
            "quantite": 1,
            "prix_unitaire": float(article["prix_vente"]),
            "stock_disponible": article["quantite_stock"],
        })
        self._rafraichir_panier()

    def _retirer_du_panier(self):
        index = self.liste_panier.currentRow()
        if index >= 0:
            self.panier.pop(index)
            self._rafraichir_panier()

    def _rafraichir_panier(self):
        self.liste_panier.clear()
        for ligne in self.panier:
            total_ligne = ligne["quantite"] * ligne["prix_unitaire"]
            texte = f"{ligne['nom']} — {ligne['quantite']} x {ligne['prix_unitaire']:.0f} FCFA = {total_ligne:.0f} FCFA"
            self.liste_panier.addItem(texte)

        if self.panier:
            sous_total, tva, total = calculer_totaux(self.panier)
        else:
            sous_total, tva, total = 0, 0, 0

        self.label_sous_total.setText(f"Sous-total HT : {sous_total:,.0f} FCFA".replace(",", " "))
        self.label_tva.setText(f"TVA (19,25%) : {tva:,.0f} FCFA".replace(",", " "))
        self.label_total.setText(f"Total à payer à la caisse : {total:,.0f} FCFA".replace(",", " "))

    # ------------------------------------------------------------
    # Enregistrement de la commande (pas de paiement à cette étape)
    # ------------------------------------------------------------
    def _enregistrer_commande(self, type_document):
        if not self.panier:
            QMessageBox.warning(self, "Panier vide", "Ajoutez au moins un article avant d'enregistrer.")
            return

        try:
            resultat = enregistrer_commande(self.utilisateur, self.panier, type_document)
        except ValueError as erreur:
            QMessageBox.critical(self, "Impossible d'enregistrer la commande", str(erreur))
            return

        chemin_pdf = self._generer_pdf(resultat, type_document)

        message = "Commande enregistrée."
        if resultat.get("numero_facture"):
            message += f"\nFacture n° {resultat['numero_facture']}"
        message += f"\nMontant à payer à la caisse : {resultat['total_ttc']:,.0f} FCFA".replace(",", " ")

        DialogueDocumentGenere("Commande enregistrée", message, chemin_pdf, parent=self).exec()

        self.panier = []
        self._rafraichir_panier()
        self.champ_recherche.clear()
        self.liste_resultats.clear()

    def _generer_pdf(self, resultat_vente, type_document):
        dossier_documents = os.path.join(os.path.expanduser("~"), "Documents", "Ventes_Quincaillerie")
        os.makedirs(dossier_documents, exist_ok=True)

        horodatage = datetime.now().strftime("%Y%m%d_%H%M%S")

        if type_document == "facture":
            nom_fichier = f"facture_{resultat_vente['numero_facture']}.pdf"
            chemin = os.path.join(dossier_documents, nom_fichier)
            generer_facture_pdf(
                chemin,
                resultat_vente["numero_facture"],
                self.panier,
                self.utilisateur["nom_complet"],
                self.utilisateur["site_nom"],
            )
        else:
            nom_fichier = f"ticket_{horodatage}.pdf"
            chemin = os.path.join(dossier_documents, nom_fichier)
            generer_ticket_pdf(
                chemin,
                self.panier,
                self.utilisateur["nom_complet"],
                self.utilisateur["site_nom"],
            )

        return chemin
