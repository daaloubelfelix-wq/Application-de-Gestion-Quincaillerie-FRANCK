from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QDoubleSpinBox, QComboBox,
    QDateEdit, QDialogButtonBox, QMessageBox
)

from database import Database
from modules.rh import creer_employe, modifier_employe, TYPES_CONTRAT


class FormulaireEmploye(QDialog):
    def __init__(self, employe=None, parent=None):
        super().__init__(parent)
        self.employe = employe  # None = création, sinon dict existant
        self.setWindowTitle("Modifier l'employé" if employe else "Ajouter un employé")
        self.setMinimumWidth(340)
        self._construire_interface()

    def _construire_interface(self):
        layout = QFormLayout()

        self.champ_nom = QLineEdit()
        self.champ_poste = QLineEdit()
        self.champ_poste.setPlaceholderText("ex : Vendeur, Magasinier...")
        self.champ_telephone = QLineEdit()

        self.champ_type_contrat = QComboBox()
        for code, libelle in TYPES_CONTRAT:
            self.champ_type_contrat.addItem(libelle, code)

        self.champ_salaire = QDoubleSpinBox()
        self.champ_salaire.setMaximum(100_000_000)
        self.champ_salaire.setSuffix(" FCFA / mois")

        self.champ_site = QComboBox()
        self.champ_site.addItem("Aucun site précis", None)
        for site in Database.fetch_all("SELECT id, nom FROM sites ORDER BY nom"):
            self.champ_site.addItem(site["nom"], site["id"])

        self.champ_date_embauche = QDateEdit()
        self.champ_date_embauche.setCalendarPopup(True)
        self.champ_date_embauche.setDate(QDate.currentDate())

        layout.addRow("Nom complet", self.champ_nom)
        layout.addRow("Poste", self.champ_poste)
        layout.addRow("Téléphone", self.champ_telephone)
        layout.addRow("Type de contrat", self.champ_type_contrat)
        layout.addRow("Salaire mensuel", self.champ_salaire)
        layout.addRow("Site", self.champ_site)
        layout.addRow("Date d'embauche", self.champ_date_embauche)

        if self.employe:
            self._pre_remplir()

        boutons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        boutons.button(QDialogButtonBox.StandardButton.Save).setText("Enregistrer")
        boutons.button(QDialogButtonBox.StandardButton.Cancel).setText("Annuler")
        boutons.accepted.connect(self._valider)
        boutons.rejected.connect(self.reject)
        layout.addRow(boutons)

        self.setLayout(layout)

    def _pre_remplir(self):
        self.champ_nom.setText(self.employe["nom_complet"])
        self.champ_poste.setText(self.employe.get("poste") or "")
        self.champ_telephone.setText(self.employe.get("telephone") or "")
        index_contrat = self.champ_type_contrat.findData(self.employe.get("type_contrat") or "permanent")
        if index_contrat >= 0:
            self.champ_type_contrat.setCurrentIndex(index_contrat)
        self.champ_salaire.setValue(float(self.employe["salaire_mensuel"]))
        if self.employe.get("site_id"):
            index = self.champ_site.findData(self.employe["site_id"])
            if index >= 0:
                self.champ_site.setCurrentIndex(index)
        if self.employe.get("date_embauche"):
            self.champ_date_embauche.setDate(QDate(self.employe["date_embauche"]))

    def _valider(self):
        try:
            if self.employe is None:
                creer_employe(
                    nom_complet=self.champ_nom.text(),
                    poste=self.champ_poste.text().strip(),
                    telephone=self.champ_telephone.text().strip(),
                    type_contrat=self.champ_type_contrat.currentData(),
                    salaire_mensuel=self.champ_salaire.value(),
                    site_id=self.champ_site.currentData(),
                    date_embauche=self.champ_date_embauche.date().toPyDate(),
                )
            else:
                modifier_employe(
                    employe_id=self.employe["id"],
                    nom_complet=self.champ_nom.text(),
                    poste=self.champ_poste.text().strip(),
                    telephone=self.champ_telephone.text().strip(),
                    type_contrat=self.champ_type_contrat.currentData(),
                    salaire_mensuel=self.champ_salaire.value(),
                    site_id=self.champ_site.currentData(),
                    date_embauche=self.champ_date_embauche.date().toPyDate(),
                )
        except ValueError as erreur:
            QMessageBox.warning(self, "Erreur de saisie", str(erreur))
            return
        self.accept()
