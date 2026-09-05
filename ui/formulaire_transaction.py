"""
Formulaire de saisie manuelle d'une transaction comptable
(dépense courante ou recette hors-vente, ex : encaissement d'une ancienne facture).
"""

from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QDoubleSpinBox, QComboBox,
    QDialogButtonBox, QMessageBox
)

from modules.comptabilite import saisir_transaction


class FormulaireTransaction(QDialog):
    def __init__(self, utilisateur, parent=None):
        super().__init__(parent)
        self.utilisateur = utilisateur
        self.setWindowTitle("Saisir une transaction")
        self.setMinimumWidth(320)
        self._construire_interface()

    def _construire_interface(self):
        layout = QFormLayout()

        self.champ_type = QComboBox()
        self.champ_type.addItem("Dépense", "depense")
        self.champ_type.addItem("Recette (hors-vente)", "recette")

        self.champ_montant = QDoubleSpinBox()
        self.champ_montant.setMaximum(100_000_000)
        self.champ_montant.setSuffix(" FCFA")

        self.champ_description = QLineEdit()
        self.champ_description.setPlaceholderText("ex : Achat fournitures bureau")

        layout.addRow("Type", self.champ_type)
        layout.addRow("Montant", self.champ_montant)
        layout.addRow("Description", self.champ_description)

        boutons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        boutons.accepted.connect(self._valider)
        boutons.rejected.connect(self.reject)
        layout.addRow(boutons)

        self.setLayout(layout)

    def _valider(self):
        try:
            saisir_transaction(
                self.utilisateur,
                self.champ_type.currentData(),
                self.champ_montant.value(),
                self.champ_description.text(),
            )
        except ValueError as erreur:
            QMessageBox.warning(self, "Erreur de saisie", str(erreur))
            return
        self.accept()
