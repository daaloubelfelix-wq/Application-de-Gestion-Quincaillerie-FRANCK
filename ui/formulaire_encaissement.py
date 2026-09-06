"""
Formulaire d'encaissement : demande le mode de paiement avant de valider
(Espèces, Orange Money, MTN Mobile Money, Crédit client, Autre).
"""

from PyQt6.QtWidgets import QDialog, QFormLayout, QLabel, QComboBox, QDialogButtonBox

from modules.paiement import MODES_PAIEMENT


class FormulaireEncaissement(QDialog):
    def __init__(self, montant_ttc, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Encaisser la commande")
        self.setMinimumWidth(320)
        self._construire_interface(montant_ttc)

    def _construire_interface(self, montant_ttc):
        layout = QFormLayout()

        label_montant = QLabel(f"{montant_ttc:,.0f} FCFA".replace(",", " "))
        label_montant.setObjectName("totalMisEnValeur")

        self.champ_mode = QComboBox()
        for code, libelle in MODES_PAIEMENT:
            self.champ_mode.addItem(libelle, code)

        layout.addRow("Montant reçu", label_montant)
        layout.addRow("Mode de paiement", self.champ_mode)

        boutons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        boutons.button(QDialogButtonBox.StandardButton.Ok).setText("Confirmer l'encaissement")
        boutons.button(QDialogButtonBox.StandardButton.Cancel).setText("Annuler")
        boutons.accepted.connect(self.accept)
        boutons.rejected.connect(self.reject)
        layout.addRow(boutons)

        self.setLayout(layout)

    def mode_paiement_selectionne(self):
        return self.champ_mode.currentData()
