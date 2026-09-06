"""
Écran Historique des ventes — réservé au responsable.

L'encaissement lui-même se fait physiquement à la caisse (hors
application) : le client paie directement au responsable, qui note à la
main sur le facturier papier ; la comptabilité saisit ensuite tout dans
l'ordinateur en une seule fois (voir modules/ventes.py::enregistrer_vente,
ui/point_de_vente.py). Cet écran sert donc à vérifier ce qui a été saisi
aujourd'hui, tous sites confondus, et à corriger une saisie erronée —
c'est pour ça que l'annulation est réservée au responsable : lui seul sait
si une correction après paiement est légitime.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)

from modules.ventes import ventes_du_jour, annuler_vente
from modules.paiement import libelle_mode_paiement
from ui.confirmation import confirmer


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
        titre = QLabel("Historique des ventes")
        titre.setObjectName("titreEcran")
        sous_titre = QLabel("Ventes du jour, tous sites confondus. Annuler seulement en cas d'erreur de saisie.")
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
        self.tableau.setColumnCount(7)
        self.tableau.setHorizontalHeaderLabels(
            ["Site", "Enregistrée par", "Document", "Montant", "Paiement", "Heure", "Action"]
        )
        self.tableau.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.tableau.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tableau.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.tableau)

        self.setLayout(layout)

    def _rafraichir(self):
        ventes = ventes_du_jour()
        self.tableau.setRowCount(len(ventes))

        for ligne, vente in enumerate(ventes):
            self.tableau.setItem(ligne, 0, QTableWidgetItem(vente["site_nom"]))
            self.tableau.setItem(ligne, 1, QTableWidgetItem(vente["enregistree_par"]))
            libelle_document = (
                f"Facture n° {vente['numero_facture']}" if vente["numero_facture"] else "Ticket"
            )
            self.tableau.setItem(ligne, 2, QTableWidgetItem(libelle_document))
            self.tableau.setItem(
                ligne, 3, QTableWidgetItem(f"{vente['total_ttc']:,.0f} FCFA".replace(",", " "))
            )
            self.tableau.setItem(ligne, 4, QTableWidgetItem(libelle_mode_paiement(vente["mode_paiement"])))
            self.tableau.setItem(ligne, 5, QTableWidgetItem(vente["date_vente"].strftime("%H:%M")))

            bouton_annuler = QPushButton("Annuler")
            bouton_annuler.setProperty("secondaire", True)
            bouton_annuler.clicked.connect(
                lambda _, vid=vente["id"]: self._annuler(vid)
            )
            self.tableau.setCellWidget(ligne, 6, bouton_annuler)

        if not ventes:
            self.tableau.setRowCount(0)

    def _annuler(self, vente_id):
        if not confirmer(
            self,
            "Confirmer l'annulation",
            "Cette vente est déjà payée : n'annulez que s'il s'agit d'une erreur de "
            "saisie. Le stock retiré sera restitué et la recette retirée. Continuer ?",
        ):
            return

        try:
            annuler_vente(vente_id, self.utilisateur)
        except ValueError as erreur:
            QMessageBox.warning(self, "Impossible d'annuler", str(erreur))
            return
        self._rafraichir()
