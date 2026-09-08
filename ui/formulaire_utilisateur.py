from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QHBoxLayout, QWidget, QLineEdit, QPushButton,
    QComboBox, QDialogButtonBox, QMessageBox
)

from database import Database
from modules.utilisateurs import creer_utilisateur
from ui.icones import icone_oeil


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

        self.bouton_oeil = QPushButton()
        self.bouton_oeil.setObjectName("boutonOeil")
        self.bouton_oeil.setCheckable(True)
        self.bouton_oeil.setIcon(icone_oeil(ouvert=False))
        self.bouton_oeil.setToolTip("Afficher le mot de passe")
        self.bouton_oeil.setFixedWidth(36)
        self.bouton_oeil.clicked.connect(self._basculer_visibilite_mot_de_passe)

        ligne_mot_de_passe = QHBoxLayout()
        ligne_mot_de_passe.setSpacing(6)
        ligne_mot_de_passe.setContentsMargins(0, 0, 0, 0)
        ligne_mot_de_passe.addWidget(self.champ_mot_de_passe)
        ligne_mot_de_passe.addWidget(self.bouton_oeil)
        conteneur_mot_de_passe = QWidget()
        conteneur_mot_de_passe.setLayout(ligne_mot_de_passe)

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
        layout.addRow("Mot de passe initial", conteneur_mot_de_passe)
        layout.addRow("Rôle", self.champ_role)
        layout.addRow("Site", self.champ_site)

        boutons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        boutons.button(QDialogButtonBox.StandardButton.Save).setText("Enregistrer")
        boutons.button(QDialogButtonBox.StandardButton.Cancel).setText("Annuler")
        boutons.accepted.connect(self._valider)
        boutons.rejected.connect(self.reject)
        layout.addRow(boutons)

        self.setLayout(layout)

    def _basculer_site(self, texte_role):
        self.champ_site.setEnabled(texte_role != "Responsable")

    def _basculer_visibilite_mot_de_passe(self):
        visible = self.bouton_oeil.isChecked()
        self.champ_mot_de_passe.setEchoMode(
            QLineEdit.EchoMode.Normal if visible else QLineEdit.EchoMode.Password
        )
        self.bouton_oeil.setIcon(icone_oeil(ouvert=visible))
        self.bouton_oeil.setToolTip("Masquer le mot de passe" if visible else "Afficher le mot de passe")

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
