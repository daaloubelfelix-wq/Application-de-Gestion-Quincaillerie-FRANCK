"""
Écran Paramètres du compte connecté : changer son identifiant et/ou son
mot de passe, réunis au même endroit (au lieu de deux boutons séparés
dans la fenêtre principale). Le mot de passe actuel est toujours requis
pour confirmer que c'est bien la personne elle-même qui fait le
changement.
"""

from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QCheckBox, QDialogButtonBox, QMessageBox
)

from modules.auth import changer_identifiant, changer_mot_de_passe, marquer_mot_de_passe_traite


class DialogueParametres(QDialog):
    def __init__(self, utilisateur, parent=None):
        super().__init__(parent)
        self.utilisateur = utilisateur
        self.setWindowTitle("Paramètres du compte")
        self.setMinimumWidth(340)
        self._construire_interface()

    def _construire_interface(self):
        layout = QFormLayout()

        self.champ_identifiant = QLineEdit()
        self.champ_identifiant.setText(self.utilisateur["identifiant"])

        self.champ_mot_de_passe_actuel = QLineEdit()
        self.champ_mot_de_passe_actuel.setEchoMode(QLineEdit.EchoMode.Password)

        self.champ_nouveau_mot_de_passe = QLineEdit()
        self.champ_nouveau_mot_de_passe.setEchoMode(QLineEdit.EchoMode.Password)
        self.champ_nouveau_mot_de_passe.setPlaceholderText("laisser vide pour ne pas changer")

        self.champ_confirmation = QLineEdit()
        self.champ_confirmation.setEchoMode(QLineEdit.EchoMode.Password)

        case_afficher = QCheckBox("Afficher les mots de passe")
        case_afficher.toggled.connect(self._basculer_visibilite)

        layout.addRow("Identifiant", self.champ_identifiant)
        layout.addRow("Mot de passe actuel", self.champ_mot_de_passe_actuel)
        layout.addRow("Nouveau mot de passe", self.champ_nouveau_mot_de_passe)
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
        self.champ_mot_de_passe_actuel.setEchoMode(mode)
        self.champ_nouveau_mot_de_passe.setEchoMode(mode)
        self.champ_confirmation.setEchoMode(mode)

    def _valider(self):
        mot_de_passe_actuel = self.champ_mot_de_passe_actuel.text()
        nouvel_identifiant = self.champ_identifiant.text().strip()
        nouveau_mot_de_passe = self.champ_nouveau_mot_de_passe.text()

        identifiant_change = nouvel_identifiant != self.utilisateur["identifiant"]
        mot_de_passe_change = bool(nouveau_mot_de_passe)

        if not identifiant_change and not mot_de_passe_change:
            QMessageBox.information(self, "Rien à changer", "Modifiez l'identifiant et/ou le mot de passe d'abord.")
            return

        if mot_de_passe_change and nouveau_mot_de_passe != self.champ_confirmation.text():
            QMessageBox.warning(self, "Erreur de saisie", "Les deux nouveaux mots de passe ne correspondent pas.")
            return

        if not mot_de_passe_actuel:
            QMessageBox.warning(self, "Erreur de saisie", "Le mot de passe actuel est requis pour confirmer.")
            return

        try:
            if identifiant_change:
                changer_identifiant(self.utilisateur["id"], mot_de_passe_actuel, nouvel_identifiant)
                self.utilisateur["identifiant"] = nouvel_identifiant
            if mot_de_passe_change:
                changer_mot_de_passe(self.utilisateur["id"], mot_de_passe_actuel, nouveau_mot_de_passe)
            else:
                marquer_mot_de_passe_traite(self.utilisateur["id"])
        except ValueError as erreur:
            QMessageBox.warning(self, "Erreur", str(erreur))
            return

        QMessageBox.information(self, "Paramètres enregistrés", "Vos informations de connexion ont été mises à jour.")
        self.accept()
