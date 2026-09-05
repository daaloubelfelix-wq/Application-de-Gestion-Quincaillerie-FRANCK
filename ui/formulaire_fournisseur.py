from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QMessageBox

from modules.fournisseurs import creer_fournisseur, modifier_fournisseur


class FormulaireFournisseur(QDialog):
    def __init__(self, fournisseur=None, parent=None):
        super().__init__(parent)
        self.fournisseur = fournisseur
        self.setWindowTitle("Modifier le fournisseur" if fournisseur else "Ajouter un fournisseur")
        self.setMinimumWidth(320)
        self._construire_interface()

    def _construire_interface(self):
        layout = QFormLayout()

        self.champ_nom = QLineEdit()
        self.champ_contact = QLineEdit()
        self.champ_telephone = QLineEdit()

        if self.fournisseur:
            self.champ_nom.setText(self.fournisseur["nom"])
            self.champ_contact.setText(self.fournisseur.get("contact") or "")
            self.champ_telephone.setText(self.fournisseur.get("telephone") or "")

        layout.addRow("Nom", self.champ_nom)
        layout.addRow("Contact", self.champ_contact)
        layout.addRow("Téléphone", self.champ_telephone)

        boutons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        boutons.accepted.connect(self._valider)
        boutons.rejected.connect(self.reject)
        layout.addRow(boutons)

        self.setLayout(layout)

    def _valider(self):
        try:
            if self.fournisseur:
                modifier_fournisseur(
                    self.fournisseur["id"],
                    self.champ_nom.text(),
                    self.champ_contact.text(),
                    self.champ_telephone.text(),
                )
            else:
                creer_fournisseur(
                    self.champ_nom.text(),
                    self.champ_contact.text(),
                    self.champ_telephone.text(),
                )
        except ValueError as erreur:
            QMessageBox.warning(self, "Erreur de saisie", str(erreur))
            return
        self.accept()
