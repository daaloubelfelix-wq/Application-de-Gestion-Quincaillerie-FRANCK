from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QComboBox, QDialogButtonBox, QMessageBox
)

from database import Database
from modules.utilisateurs import creer_utilisateur


class FormulaireUtilisateur(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Créer un compte")
        self.setMinimumWidth(320)
        self._construire_interface()

    def _construire_interface(self):
        layout = QFormLayout()

        self.champ_nom = QLineEdit()
        self.champ_identifiant = QLineEdit()
        self.champ_identifiant.setPlaceholderText("ex : a.kone")
        self.champ_mot_de_passe = QLineEdit()
        self.champ_mot_de_passe.setEchoMode(QLineEdit.EchoMode.Password)

        self.champ_role = QComboBox()
        self.champ_role.addItem("Agent stock", "agent_stock")
        self.champ_role.addItem("Agent comptabilité", "agent_comptabilite")
        self.champ_role.addItem("Responsable", "responsable")
        self.champ_role.currentTextChanged.connect(self._basculer_site)

        self.champ_site = QComboBox()
        for site in Database.fetch_all("SELECT id, nom FROM sites ORDER BY nom"):
            self.champ_site.addItem(site["nom"], site["id"])

        layout.addRow("Nom complet", self.champ_nom)
        layout.addRow("Identifiant", self.champ_identifiant)
        layout.addRow("Mot de passe initial", self.champ_mot_de_passe)
        layout.addRow("Rôle", self.champ_role)
        layout.addRow("Site", self.champ_site)

        boutons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        boutons.accepted.connect(self._valider)
        boutons.rejected.connect(self.reject)
        layout.addRow(boutons)

        self.setLayout(layout)

    def _basculer_site(self, texte_role):
        self.champ_site.setEnabled(texte_role != "Responsable")

    def _valider(self):
        try:
            creer_utilisateur(
                nom_complet=self.champ_nom.text(),
                identifiant=self.champ_identifiant.text(),
                mot_de_passe=self.champ_mot_de_passe.text(),
                role=self.champ_role.currentData(),
                site_id=self.champ_site.currentData(),
            )
        except ValueError as erreur:
            QMessageBox.warning(self, "Erreur de saisie", str(erreur))
            return
        self.accept()
