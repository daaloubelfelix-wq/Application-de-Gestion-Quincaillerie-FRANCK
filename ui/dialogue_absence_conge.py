from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QComboBox, QDateEdit,
    QDialogButtonBox, QMessageBox
)

from modules.rh import enregistrer_absence_conge


class DialogueAbsenceConge(QDialog):
    def __init__(self, employe, utilisateur, parent=None):
        super().__init__(parent)
        self.employe = employe
        self.utilisateur = utilisateur
        self.setWindowTitle(f"Absence / congé — {employe['nom_complet']}")
        self.setMinimumWidth(320)
        self._construire_interface()

    def _construire_interface(self):
        layout = QFormLayout()

        self.champ_type = QComboBox()
        self.champ_type.addItem("Absence", "absence")
        self.champ_type.addItem("Congé", "conge")

        self.champ_date_debut = QDateEdit()
        self.champ_date_debut.setCalendarPopup(True)
        self.champ_date_debut.setDate(QDate.currentDate())

        self.champ_date_fin = QDateEdit()
        self.champ_date_fin.setCalendarPopup(True)
        self.champ_date_fin.setDate(QDate.currentDate())

        self.champ_motif = QLineEdit()
        self.champ_motif.setPlaceholderText("ex : Maladie, congé annuel...")

        layout.addRow("Type", self.champ_type)
        layout.addRow("Du", self.champ_date_debut)
        layout.addRow("Au", self.champ_date_fin)
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
            enregistrer_absence_conge(
                employe_id=self.employe["id"],
                type_evenement=self.champ_type.currentData(),
                date_debut=self.champ_date_debut.date().toPyDate(),
                date_fin=self.champ_date_fin.date().toPyDate(),
                motif=self.champ_motif.text().strip(),
                utilisateur_id=self.utilisateur["id"],
            )
        except ValueError as erreur:
            QMessageBox.warning(self, "Erreur de saisie", str(erreur))
            return
        self.accept()
