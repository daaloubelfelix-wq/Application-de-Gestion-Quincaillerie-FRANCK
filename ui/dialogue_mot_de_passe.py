"""
Dialogue permettant à n'importe quel utilisateur connecté de changer
lui-même son mot de passe (bouton "Modifier mon mot de passe" de la
fenêtre principale) — chacun choisit et garde son propre mot de passe,
au lieu que ce soit toujours le responsable qui le fixe.
"""

from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QHBoxLayout, QWidget, QLineEdit, QPushButton,
    QDialogButtonBox, QMessageBox, QCheckBox
)

from modules.auth import changer_mot_de_passe
from ui.icones import icone_oeil


class DialogueMotDePasse(QDialog):
    def __init__(self, utilisateur, parent=None):
        super().__init__(parent)
        self.utilisateur = utilisateur
        self.setWindowTitle("Modifier mon mot de passe")
        self.setMinimumWidth(320)
        self._construire_interface()

    def _construire_interface(self):
        layout = QFormLayout()

        self.champ_ancien = QLineEdit()
        self.champ_ancien.setEchoMode(QLineEdit.EchoMode.Password)
        self.champ_nouveau = QLineEdit()
        self.champ_nouveau.setEchoMode(QLineEdit.EchoMode.Password)
        self.champ_confirmation = QLineEdit()
        self.champ_confirmation.setEchoMode(QLineEdit.EchoMode.Password)

        case_afficher = QCheckBox("Afficher les mots de passe")
        case_afficher.toggled.connect(self._basculer_visibilite)

        layout.addRow("Mot de passe actuel", self.champ_ancien)
        layout.addRow("Nouveau mot de passe", self.champ_nouveau)
        layout.addRow("Confirmer le nouveau", self.champ_confirmation)
        layout.addRow("", case_afficher)

        boutons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        boutons.button(QDialogButtonBox.StandardButton.Save).setText("Enregistrer")
        boutons.button(QDialogButtonBox.StandardButton.Cancel).setText("Annuler")
        boutons.accepted.connect(self._valider)
        boutons.rejected.connect(self.reject)
        layout.addRow(boutons)

        self.setLayout(layout)

    def _basculer_visibilite(self, visible):
        mode = QLineEdit.EchoMode.Normal if visible else QLineEdit.EchoMode.Password
        self.champ_ancien.setEchoMode(mode)
        self.champ_nouveau.setEchoMode(mode)
        self.champ_confirmation.setEchoMode(mode)

    def _valider(self):
        if self.champ_nouveau.text() != self.champ_confirmation.text():
            QMessageBox.warning(self, "Erreur de saisie", "Les deux nouveaux mots de passe ne correspondent pas.")
            return

        try:
            changer_mot_de_passe(
                self.utilisateur["id"], self.champ_ancien.text(), self.champ_nouveau.text()
            )
        except ValueError as erreur:
            QMessageBox.warning(self, "Erreur", str(erreur))
            return

        QMessageBox.information(self, "Mot de passe modifié", "Votre mot de passe a bien été mis à jour.")
        self.accept()
