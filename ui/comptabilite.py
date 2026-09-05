"""
Écran de comptabilité.
Les recettes issues des ventes apparaissent automatiquement ;
le bouton "Saisir" sert uniquement aux dépenses et recettes hors-vente.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtGui import QColor

from modules.comptabilite import totaux_du_jour, historique_transactions
from ui.formulaire_transaction import FormulaireTransaction


class Comptabilite(QWidget):
    def __init__(self, utilisateur):
        super().__init__()
        self.utilisateur = utilisateur
        self._construire_interface()
        self._rafraichir()

    def _construire_interface(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        entete = QHBoxLayout()
        titre = QLabel(f"Comptabilité · {self.utilisateur['site_nom']}")
        titre.setStyleSheet("font-size: 15px; font-weight: bold;")
        bouton_saisir = QPushButton("+ Saisir")
        bouton_saisir.clicked.connect(self._ouvrir_formulaire)
        entete.addWidget(titre)
        entete.addStretch()
        entete.addWidget(bouton_saisir)
        layout.addLayout(entete)

        cartes = QHBoxLayout()
        self.carte_recettes = self._creer_carte("Recettes du jour", "#DEE9DF", "#43724A")
        self.carte_depenses = self._creer_carte("Dépenses du jour", "#F4DDD0", "#A8431C")
        cartes.addWidget(self.carte_recettes)
        cartes.addWidget(self.carte_depenses)
        layout.addLayout(cartes)

        self.cadre_solde = QFrame()
        self.cadre_solde.setStyleSheet("background-color: #EAE5D7; border-radius: 8px; padding: 12px;")
        solde_layout = QHBoxLayout()
        self.label_solde_titre = QLabel("Solde net du jour")
        self.label_solde_valeur = QLabel("0 FCFA")
        self.label_solde_valeur.setStyleSheet("font-size: 18px; font-weight: bold;")
        solde_layout.addWidget(self.label_solde_titre)
        solde_layout.addStretch()
        solde_layout.addWidget(self.label_solde_valeur)
        self.cadre_solde.setLayout(solde_layout)
        layout.addWidget(self.cadre_solde)

        titre_historique = QLabel("Historique")
        titre_historique.setStyleSheet("font-size: 13px; font-weight: bold;")
        layout.addWidget(titre_historique)

        self.tableau = QTableWidget()
        self.tableau.setColumnCount(4)
        self.tableau.setHorizontalHeaderLabels(["Description", "Auteur", "Date", "Montant"])
        self.tableau.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tableau.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.tableau)

        self.setLayout(layout)

    def _creer_carte(self, titre, couleur_fond, couleur_texte):
        cadre = QFrame()
        cadre.setStyleSheet(f"background-color: {couleur_fond}; border-radius: 8px; padding: 12px;")
        vlayout = QVBoxLayout()
        label_titre = QLabel(titre)
        label_titre.setStyleSheet(f"font-size: 12px; color: {couleur_texte};")
        label_valeur = QLabel("0 FCFA")
        label_valeur.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {couleur_texte};")
        label_valeur.setObjectName("valeur")
        vlayout.addWidget(label_titre)
        vlayout.addWidget(label_valeur)
        cadre.setLayout(vlayout)
        return cadre

    def _rafraichir(self):
        totaux = totaux_du_jour(self.utilisateur["site_id"])

        self.carte_recettes.findChild(QLabel, "valeur").setText(
            f"{totaux['recettes']:,.0f} FCFA".replace(",", " ")
        )
        self.carte_depenses.findChild(QLabel, "valeur").setText(
            f"{totaux['depenses']:,.0f} FCFA".replace(",", " ")
        )
        self.label_solde_valeur.setText(f"{totaux['solde_net']:,.0f} FCFA".replace(",", " "))

        transactions = historique_transactions(self.utilisateur["site_id"])
        self.tableau.setRowCount(len(transactions))
        for ligne, transaction in enumerate(transactions):
            self.tableau.setItem(ligne, 0, QTableWidgetItem(transaction["description"] or "—"))
            self.tableau.setItem(ligne, 1, QTableWidgetItem(transaction["auteur"]))
            self.tableau.setItem(
                ligne, 2, QTableWidgetItem(transaction["date_transaction"].strftime("%d/%m/%Y %H:%M"))
            )

            signe = "+" if transaction["type"] == "recette" else "-"
            item_montant = QTableWidgetItem(f"{signe}{transaction['montant']:,.0f} FCFA".replace(",", " "))
            item_montant.setForeground(
                QColor("#43724A") if transaction["type"] == "recette" else QColor("#A8431C")
            )
            self.tableau.setItem(ligne, 3, item_montant)

    def _ouvrir_formulaire(self):
        dialogue = FormulaireTransaction(self.utilisateur, parent=self)
        if dialogue.exec():
            self._rafraichir()
