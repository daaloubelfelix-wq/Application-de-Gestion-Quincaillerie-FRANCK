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
    QListWidget, QListWidgetItem, QMessageBox, QComboBox, QFrame, QSpinBox,
    QSizePolicy
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
            "Le prix est celui négocié par le responsable avec le client et "
            "inscrit sur le facturier papier — saisissez-le tel quel, il peut "
            "différer du prix catalogue."
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
        self.liste_resultats.currentItemChanged.connect(self._sur_selection_resultat)
        layout.addWidget(self.liste_resultats)

        # Quantité + prix (celui du facturier papier, pas forcément le prix
        # catalogue) + ajout au panier.
        ligne_quantite = QHBoxLayout()
        ligne_quantite.addWidget(QLabel("Quantité :"))
        self.champ_quantite = QSpinBox()
        self.champ_quantite.setRange(0, 99999)
        self.champ_quantite.setValue(0)
        self.champ_quantite.setSpecialValueText(" ")
        ligne_quantite.addWidget(self.champ_quantite)
        ligne_quantite.addWidget(QLabel("Prix unitaire (FCFA) :"))
        self.champ_prix = QSpinBox()
        self.champ_prix.setRange(0, 999_999_999)
        self.champ_prix.setValue(0)
        self.champ_prix.setSpecialValueText(" ")
        ligne_quantite.addWidget(self.champ_prix)
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
        self.liste_panier.setMinimumHeight(60)
        layout.addWidget(self.liste_panier)

        bouton_retirer = QPushButton("Retirer l'article sélectionné")
        bouton_retirer.setProperty("secondaire", True)
        bouton_retirer.clicked.connect(self._retirer_du_panier)
        layout.addWidget(bouton_retirer)

        # Récapitulatif des totaux + mode de paiement — hauteur fixée à sa
        # taille naturelle : si la fenêtre est trop petite, c'est la liste
        # du panier (au-dessus, extensible) qui doit se comprimer en
        # premier, jamais ce bloc, sinon le texte des lignes se chevauche.
        self.cadre_totaux = QFrame()
        self.cadre_totaux.setObjectName("carteTotaux")
        self.cadre_totaux.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
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
        # Construit chaque ligne à la main (plutôt qu'un QFormLayout) pour
        # garantir un espacement vertical net et fiable entre les lignes,
        # quel que soit le style visuel du système d'exploitation.
        colonne = QVBoxLayout()
        colonne.setContentsMargins(4, 8, 4, 8)
        colonne.setSpacing(16)

        self.label_sous_total = QLabel("0 FCFA")
        self.label_tva = QLabel("0 FCFA")
        self.label_total = QLabel("0 FCFA")
        self.label_total.setObjectName("totalMisEnValeur")

        self.selecteur_mode_paiement = QComboBox()
        for code, libelle in MODES_PAIEMENT:
            self.selecteur_mode_paiement.addItem(libelle, code)

        def ligne(texte_etiquette, widget_valeur):
            rangee = QHBoxLayout()
            rangee.setSpacing(18)
            etiquette = QLabel(texte_etiquette)
            rangee.addWidget(etiquette)
            rangee.addStretch()
            rangee.addWidget(widget_valeur)
            colonne.addLayout(rangee)

        ligne("Sous-total HT :", self.label_sous_total)
        ligne(f"TVA ({TAUX_TVA}%) :", self.label_tva)
        ligne("Total payé par le client :", self.label_total)
        ligne("Mode de paiement (indiqué sur le facturier) :", self.selecteur_mode_paiement)
        self.cadre_totaux.setLayout(colonne)

    # ------------------------------------------------------------
    # Recherche et gestion du panier
    # ------------------------------------------------------------
    def _rechercher(self, texte):
        self.liste_resultats.clear()
        if len(texte.strip()) < 2:
            return
        for article in rechercher_articles(self.utilisateur["site_id"], texte.strip()):
            prix_indicatif = f"{article['prix_vente']:.0f} FCFA (catalogue)" if article["prix_vente"] > 0 else "prix à saisir"
            libelle = f"{article['nom']} — {prix_indicatif} ({article['quantite_stock']} en stock)"
            item = QListWidgetItem(libelle)
            item.setData(Qt.ItemDataRole.UserRole, article)
            self.liste_resultats.addItem(item)

    def _sur_selection_resultat(self, item, item_precedent=None):
        if item is None:
            return
        article = item.data(Qt.ItemDataRole.UserRole)
        self.champ_prix.setValue(int(article["prix_vente"]))

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
        prix_saisi = self.champ_prix.value()

        if quantite_demandee <= 0:
            QMessageBox.information(self, "Quantité manquante", "Indiquez d'abord une quantité.")
            return

        if prix_saisi <= 0:
            QMessageBox.information(
                self, "Prix manquant",
                "Indiquez le prix inscrit sur le facturier papier avant d'ajouter l'article."
            )
            return

        if article["quantite_stock"] <= 0:
            QMessageBox.warning(self, "Rupture de stock", f"'{article['nom']}' n'est plus en stock.")
            return

        # Si déjà dans le panier, on augmente juste la quantité (même ligne
        # du facturier, donc même prix — celui déjà enregistré est conservé).
        for ligne in self.panier:
            if ligne["article_id"] == article["id"]:
                nouvelle_quantite = ligne["quantite"] + quantite_demandee
                if nouvelle_quantite > article["quantite_stock"]:
                    QMessageBox.warning(self, "Stock insuffisant", f"Stock disponible : {article['quantite_stock']}.")
                    return
                ligne["quantite"] = nouvelle_quantite
                self._rafraichir_panier()
                self.champ_quantite.setValue(0)
                return

        if quantite_demandee > article["quantite_stock"]:
            QMessageBox.warning(self, "Stock insuffisant", f"Stock disponible : {article['quantite_stock']}.")
            return

        self.panier.append({
            "article_id": article["id"],
            "nom": article["nom"],
            "quantite": quantite_demandee,
            "prix_unitaire": float(prix_saisi),
            "stock_disponible": article["quantite_stock"],
        })
        self._rafraichir_panier()
        self.champ_quantite.setValue(0)
        self.champ_prix.setValue(0)

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

        self.label_sous_total.setText(f"{sous_total:,.0f} FCFA".replace(",", " "))
        self.label_tva.setText(f"{tva:,.0f} FCFA".replace(",", " "))
        self.label_total.setText(f"{total:,.0f} FCFA".replace(",", " "))

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
