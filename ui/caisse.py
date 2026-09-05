"""
Écran de caisse — réservé au responsable.
Liste les commandes enregistrées par la comptabilité et en attente de
paiement ; le client vient payer ici. C'est cet écran qui crée la recette
comptable (voir modules/ventes.py, encaisser_commande).
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)

from modules.ventes import commandes_en_attente, encaisser_commande, annuler_commande


class Caisse(QWidget):
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
        titre = QLabel("Caisse")
        titre.setObjectName("titreEcran")
        sous_titre = QLabel("Commandes en attente de paiement, tous sites confondus.")
        sous_titre.setObjectName("texteAttenue")
        colonne_titres = QVBoxLayout()
        colonne_titres.addWidget(titre)
        colonne_titres.addWidget(sous_titre)
        entete.addLayout(colonne_titres)
        entete.addStretch()
        bouton_rafraichir = QPushButton("Rafraîchir")
        bouton_rafraichir.setProperty("secondaire", True)
        bouton_rafraichir.clicked.connect(self._rafraichir)
        entete.addWidget(bouton_rafraichir)
        layout.addLayout(entete)

        self.tableau = QTableWidget()
        self.tableau.setColumnCount(6)
        self.tableau.setHorizontalHeaderLabels(
            ["Site", "Enregistrée par", "Document", "Montant", "Heure", "Action"]
        )
        self.tableau.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.tableau.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tableau.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.tableau)

        self.setLayout(layout)

    def _rafraichir(self):
        commandes = commandes_en_attente()
        self.tableau.setRowCount(len(commandes))

        for ligne, commande in enumerate(commandes):
            self.tableau.setItem(ligne, 0, QTableWidgetItem(commande["site_nom"]))
            self.tableau.setItem(ligne, 1, QTableWidgetItem(commande["enregistree_par"]))
            libelle_document = (
                f"Facture n° {commande['numero_facture']}"
                if commande["numero_facture"] else "Ticket"
            )
            self.tableau.setItem(ligne, 2, QTableWidgetItem(libelle_document))
            self.tableau.setItem(
                ligne, 3, QTableWidgetItem(f"{commande['total_ttc']:,.0f} FCFA".replace(",", " "))
            )
            self.tableau.setItem(ligne, 4, QTableWidgetItem(commande["date_vente"].strftime("%H:%M")))

            actions = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(0, 0, 0, 0)
            bouton_encaisser = QPushButton("Encaisser")
            bouton_encaisser.clicked.connect(
                lambda _, vid=commande["id"]: self._encaisser(vid)
            )
            bouton_annuler = QPushButton("Annuler")
            bouton_annuler.setProperty("secondaire", True)
            bouton_annuler.clicked.connect(
                lambda _, vid=commande["id"]: self._annuler(vid)
            )
            actions_layout.addWidget(bouton_encaisser)
            actions_layout.addWidget(bouton_annuler)
            actions.setLayout(actions_layout)
            self.tableau.setCellWidget(ligne, 5, actions)

        if not commandes:
            self.tableau.setRowCount(0)

    def _encaisser(self, vente_id):
        try:
            resultat = encaisser_commande(vente_id, self.utilisateur)
        except ValueError as erreur:
            QMessageBox.warning(self, "Impossible d'encaisser", str(erreur))
            return
        QMessageBox.information(
            self, "Paiement reçu",
            f"Encaissement enregistré : {resultat['total_ttc']:,.0f} FCFA".replace(",", " "),
        )
        self._rafraichir()

    def _annuler(self, vente_id):
        reponse = QMessageBox.question(
            self,
            "Confirmer l'annulation",
            "Le client ne paie pas cette commande — le stock retiré sera restitué. Continuer ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reponse != QMessageBox.StandardButton.Yes:
            return

        try:
            annuler_commande(vente_id, self.utilisateur)
        except ValueError as erreur:
            QMessageBox.warning(self, "Impossible d'annuler", str(erreur))
            return
        self._rafraichir()
