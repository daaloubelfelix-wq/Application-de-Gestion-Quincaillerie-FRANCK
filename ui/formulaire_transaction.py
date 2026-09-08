"""
Formulaire de saisie manuelle d'une transaction comptable
(dépense courante ou recette hors-vente, ex : encaissement d'une ancienne facture).

Pour une dépense de type salaire, on choisit l'employé dans une liste
(au lieu d'écrire un texte libre) — ça donne une vraie traçabilité,
voir modules/rh.py et modules/comptabilite.py::saisir_transaction.
"""

from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QDoubleSpinBox, QComboBox,
    QDialogButtonBox, QMessageBox
)

from modules.comptabilite import saisir_transaction
from modules.rh import lister_employes


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

        self.champ_employe = QComboBox()
        self.champ_employe.addItem("Aucun (dépense courante)", None)
        for employe in lister_employes(actifs_seulement=True):
            self.champ_employe.addItem(employe["nom_complet"], employe["id"])
        self.champ_employe.currentIndexChanged.connect(self._sur_choix_employe)

        self.champ_description = QLineEdit()
        self.champ_description.setPlaceholderText("ex : Achat fournitures bureau")

        layout.addRow("Type", self.champ_type)
        layout.addRow("Montant", self.champ_montant)
        layout.addRow("Salaire de (si c'est une paie)", self.champ_employe)
        layout.addRow("Description", self.champ_description)

        boutons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        boutons.button(QDialogButtonBox.StandardButton.Save).setText("Enregistrer")
        boutons.button(QDialogButtonBox.StandardButton.Cancel).setText("Annuler")
        boutons.accepted.connect(self._valider)
        boutons.rejected.connect(self.reject)
        layout.addRow(boutons)

        self.setLayout(layout)

    def _sur_choix_employe(self):
        nom_employe = self.champ_employe.currentText()
        if self.champ_employe.currentData() is not None and not self.champ_description.text().strip():
            self.champ_description.setText(f"Salaire — {nom_employe}")

    def _valider(self):
        try:
            saisir_transaction(
                self.utilisateur,
                self.champ_type.currentData(),
                self.champ_montant.value(),
                self.champ_description.text(),
                employe_id=self.champ_employe.currentData(),
            )
        except ValueError as erreur:
            QMessageBox.warning(self, "Erreur de saisie", str(erreur))
            return
        self.accept()
