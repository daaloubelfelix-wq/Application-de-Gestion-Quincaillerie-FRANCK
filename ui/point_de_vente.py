"""
Écran d'enregistrement d'une vente (tenu par la comptabilité).

Circuit réel de la boutique : le client a déjà payé directement à la
caisse (le responsable note à la main sur le facturier papier) ; la
comptabilité saisit ensuite tout ici, en une seule fois, à partir de
cette note. C'est cette saisie qui retire le stock, crée la recette,
attribue le numéro de facture si nécessaire, ET imprime directement le
reçu final (format imprimante ticket, deux copies) — voir
modules/ventes.py::enregistrer_vente.
"""

import os
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QMessageBox, QComboBox, QFrame, QSpinBox
)
from PyQt6.QtCore import Qt

from modules.ventes import enregistrer_vente, rechercher_articles
from modules.facturation import calculer_totaux, generer_recu_thermique_pdf, TAUX_TVA
from modules.paiement import MODES_PAIEMENT
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

        titre = QLabel(f"Enregistrer une vente · {self.utilisateur['site_nom']}")
        titre.setObjectName("titreEcran")
        layout.addWidget(titre)

        sous_titre = QLabel(
            "Le client a déjà payé à la caisse. Saisissez ici ce qui est indiqué "
            "sur le facturier papier, puis enregistrez."
        )
        sous_titre.setObjectName("texteAttenue")
        sous_titre.setWordWrap(True)
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

        # Quantité + ajout au panier — on choisit la quantité une seule
        # fois, pas besoin de cliquer plusieurs fois pour une grande quantité.
        ligne_quantite = QHBoxLayout()
        ligne_quantite.addWidget(QLabel("Quantité :"))
        self.champ_quantite = QSpinBox()
        self.champ_quantite.setRange(1, 99999)
        self.champ_quantite.setValue(1)
        ligne_quantite.addWidget(self.champ_quantite)
        bouton_ajouter = QPushButton("Ajouter au panier")
        bouton_ajouter.clicked.connect(self._ajouter_selection_au_panier)
        ligne_quantite.addWidget(bouton_ajouter)
        ligne_quantite.addStretch()
        layout.addLayout(ligne_quantite)

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

        # Récapitulatif des totaux + mode de paiement
        self.cadre_totaux = QFrame()
        self.cadre_totaux.setObjectName("carteTotaux")
        self._construire_zone_totaux()
        layout.addWidget(self.cadre_totaux)

        # Boutons d'enregistrement de la vente
        actions = QHBoxLayout()
        bouton_ticket = QPushButton("Enregistrer — Ticket")
        bouton_ticket.clicked.connect(lambda: self._enregistrer_vente("ticket"))
        bouton_facture = QPushButton("Enregistrer — Facture détaillée")
        bouton_facture.clicked.connect(lambda: self._enregistrer_vente("facture"))
        actions.addWidget(bouton_ticket)
        actions.addWidget(bouton_facture)
        layout.addLayout(actions)

        self.setLayout(layout)

    def _construire_zone_totaux(self):
        vlayout = QVBoxLayout()
        self.label_sous_total = QLabel("Sous-total HT : 0 FCFA")
        self.label_tva = QLabel(f"TVA ({TAUX_TVA}%) : 0 FCFA")
        self.label_total = QLabel("Total payé par le client : 0 FCFA")
        self.label_total.setObjectName("totalMisEnValeur")

        ligne_mode_paiement = QHBoxLayout()
        libelle_mode = QLabel("Mode de paiement (indiqué sur le facturier) :")
        self.selecteur_mode_paiement = QComboBox()
        for code, libelle in MODES_PAIEMENT:
            self.selecteur_mode_paiement.addItem(libelle, code)
        ligne_mode_paiement.addWidget(libelle_mode)
        ligne_mode_paiement.addWidget(self.selecteur_mode_paiement)

        vlayout.addWidget(self.label_sous_total)
        vlayout.addWidget(self.label_tva)
        vlayout.addWidget(self.label_total)
        vlayout.addLayout(ligne_mode_paiement)
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

    def _ajouter_selection_au_panier(self):
        item = self.liste_resultats.currentItem()
        if item is None:
            QMessageBox.information(
                self, "Aucun article sélectionné",
                "Sélectionnez d'abord un article dans la liste des résultats."
            )
            return
        self._ajouter_au_panier(item)

    def _ajouter_au_panier(self, item):
        article = item.data(Qt.ItemDataRole.UserRole)
        quantite_demandee = self.champ_quantite.value()

        if article["quantite_stock"] <= 0:
            QMessageBox.warning(self, "Rupture de stock", f"'{article['nom']}' n'est plus en stock.")
            return

        # Si déjà dans le panier, on augmente juste la quantité
        for ligne in self.panier:
            if ligne["article_id"] == article["id"]:
                nouvelle_quantite = ligne["quantite"] + quantite_demandee
                if nouvelle_quantite > article["quantite_stock"]:
                    QMessageBox.warning(self, "Stock insuffisant", f"Stock disponible : {article['quantite_stock']}.")
                    return
                ligne["quantite"] = nouvelle_quantite
                self._rafraichir_panier()
                self.champ_quantite.setValue(1)
                return

        if quantite_demandee > article["quantite_stock"]:
            QMessageBox.warning(self, "Stock insuffisant", f"Stock disponible : {article['quantite_stock']}.")
            return

        self.panier.append({
            "article_id": article["id"],
            "nom": article["nom"],
            "quantite": quantite_demandee,
            "prix_unitaire": float(article["prix_vente"]),
            "stock_disponible": article["quantite_stock"],
        })
        self._rafraichir_panier()
        self.champ_quantite.setValue(1)

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
        self.label_tva.setText(f"TVA ({TAUX_TVA}%) : {tva:,.0f} FCFA".replace(",", " "))
        self.label_total.setText(f"Total payé par le client : {total:,.0f} FCFA".replace(",", " "))

    # ------------------------------------------------------------
    # Enregistrement de la vente (déjà payée à la caisse)
    # ------------------------------------------------------------
    def _enregistrer_vente(self, type_document):
        if not self.panier:
            QMessageBox.warning(self, "Panier vide", "Ajoutez au moins un article avant d'enregistrer.")
            return

        mode_paiement = self.selecteur_mode_paiement.currentData()

        try:
            resultat = enregistrer_vente(self.utilisateur, self.panier, type_document, mode_paiement)
        except ValueError as erreur:
            QMessageBox.critical(self, "Impossible d'enregistrer la vente", str(erreur))
            return

        chemin_pdf = self._generer_recu(resultat)

        message = f"Vente enregistrée : {resultat['total_ttc']:,.0f} FCFA".replace(",", " ")
        if resultat.get("numero_facture"):
            message += f"\nFacture n° {resultat['numero_facture']}"

        DialogueDocumentGenere("Vente enregistrée", message, chemin_pdf, parent=self).exec()

        self.panier = []
        self._rafraichir_panier()
        self.champ_recherche.clear()
        self.liste_resultats.clear()

    def _generer_recu(self, resultat):
        dossier_documents = os.path.join(os.path.expanduser("~"), "Documents", "Ventes_Quincaillerie")
        os.makedirs(dossier_documents, exist_ok=True)

        if resultat["type_document"] == "facture":
            date_du_jour = datetime.now().strftime("%Y-%m-%d")
            nom_fichier = f"Facture n° {resultat['numero_facture']} - {date_du_jour}.pdf"
        else:
            horodatage = datetime.now().strftime("%Y-%m-%d %Hh%M")
            nom_fichier = f"Ticket {horodatage}.pdf"
        chemin = os.path.join(dossier_documents, nom_fichier)

        generer_recu_thermique_pdf(
            chemin, resultat["id"], resultat["type_document"], resultat["numero_facture"], resultat["lignes"],
            resultat["vendeur_nom"], resultat["mode_paiement"], resultat["site_nom"],
        )
        return chemin
