from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QDoubleSpinBox, QDialogButtonBox, QMessageBox
)

from modules.rh import enregistrer_avance


class DialogueAvanceSalaire(QDialog):
    def __init__(self, employe, utilisateur, parent=None):
        super().__init__(parent)
        self.employe = employe
        self.utilisateur = utilisateur
        self.setWindowTitle(f"Avance sur salaire — {employe['nom_complet']}")
        self.setMinimumWidth(320)
        self._construire_interface()

    def _construire_interface(self):
        layout = QFormLayout()

        self.champ_montant = QDoubleSpinBox()
        self.champ_montant.setMaximum(100_000_000)
        self.champ_montant.setSuffix(" FCFA")

        self.champ_motif = QLineEdit()
        self.champ_motif.setPlaceholderText("ex : Avance pour urgence familiale")

        layout.addRow("Montant de l'avance", self.champ_montant)
        layout.addRow("Motif", self.champ_motif)

        boutons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        boutons.button(QDialogButtonBox.StandardButton.Save).setText("Enregistrer")
        boutons.button(QDialogButtonBox.StandardButton.Cancel).setText("Annuler")
        boutons.accepted.connect(self._valider)
        boutons.rejected.connect(self.reject)
        layout.addRow(boutons)

        self.setLayout(layout)

    def _valider(self):
        try:
            enregistrer_avance(
                employe_id=self.employe["id"],
                montant=self.champ_montant.value(),
                motif=self.champ_motif.text().strip(),
                utilisateur_id=self.utilisateur["id"],
            )
        except ValueError as erreur:
            QMessageBox.warning(self, "Erreur de saisie", str(erreur))
            return
        self.accept()
