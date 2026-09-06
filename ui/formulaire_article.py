"""
Formulaire d'ajout ou de modification d'un article.
Réutilisé pour la création (article=None) et la modification (article fourni).
"""

from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QDoubleSpinBox, QSpinBox,
    QComboBox, QDialogButtonBox, QMessageBox
)

from modules.articles import creer_article, modifier_article, lister_fournisseurs

UNITES_DISPONIBLES = ["sac", "barre", "unité", "m3", "litre", "kg", "rouleau", "bidon"]


class FormulaireArticle(QDialog):
    def __init__(self, utilisateur, article=None, parent=None):
        super().__init__(parent)
        self.utilisateur = utilisateur
        self.article = article  # None = création, sinon dict existant
        self.setWindowTitle("Modifier l'article" if article else "Ajouter un article")
        self.setMinimumWidth(360)
        self._construire_interface()

    def _construire_interface(self):
        layout = QFormLayout()

        self.champ_nom = QLineEdit()
        self.champ_categorie = QLineEdit()
        self.champ_unite = QComboBox()
        self.champ_unite.addItems(UNITES_DISPONIBLES)
        self.champ_unite.setEditable(True)

        self.champ_prix_achat = QDoubleSpinBox()
        self.champ_prix_achat.setMaximum(100_000_000)
        self.champ_prix_achat.setSuffix(" FCFA")

        self.champ_prix_vente = QDoubleSpinBox()
        self.champ_prix_vente.setMaximum(100_000_000)
        self.champ_prix_vente.setSuffix(" FCFA")

        self.champ_seuil_alerte = QSpinBox()
        self.champ_seuil_alerte.setMaximum(100_000)
        self.champ_seuil_alerte.setValue(5)

        self.champ_fournisseur = QComboBox()
        self.champ_fournisseur.addItem("Aucun", None)
        for fournisseur in lister_fournisseurs():
            self.champ_fournisseur.addItem(fournisseur["nom"], fournisseur["id"])

        layout.addRow("Nom de l'article", self.champ_nom)
        layout.addRow("Catégorie", self.champ_categorie)
        layout.addRow("Unité", self.champ_unite)
        layout.addRow("Prix d'achat", self.champ_prix_achat)
        layout.addRow("Prix de vente", self.champ_prix_vente)
        layout.addRow("Seuil d'alerte", self.champ_seuil_alerte)
        layout.addRow("Fournisseur", self.champ_fournisseur)

        if self.article is None:
            self.champ_quantite_initiale = QSpinBox()
            self.champ_quantite_initiale.setMaximum(1_000_000)
            layout.addRow("Quantité initiale", self.champ_quantite_initiale)
        else:
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
        self.champ_nom.setText(self.article["nom"])
        self.champ_categorie.setText(self.article.get("categorie") or "")
        self.champ_unite.setCurrentText(self.article["unite"])
        self.champ_prix_achat.setValue(float(self.article["prix_achat"]))
        self.champ_prix_vente.setValue(float(self.article["prix_vente"]))
        self.champ_seuil_alerte.setValue(self.article["seuil_alerte"])
        if self.article.get("fournisseur_id"):
            index = self.champ_fournisseur.findData(self.article["fournisseur_id"])
            if index >= 0:
                self.champ_fournisseur.setCurrentIndex(index)

    def _valider(self):
        try:
            if self.article is None:
                creer_article(
                    site_id=self.utilisateur["site_id"],
                    nom=self.champ_nom.text(),
                    categorie=self.champ_categorie.text().strip() or None,
                    unite=self.champ_unite.currentText(),
                    prix_achat=self.champ_prix_achat.value(),
                    prix_vente=self.champ_prix_vente.value(),
                    quantite_initiale=self.champ_quantite_initiale.value(),
                    seuil_alerte=self.champ_seuil_alerte.value(),
                    fournisseur_id=self.champ_fournisseur.currentData(),
                )
            else:
                modifier_article(
                    article_id=self.article["id"],
                    nom=self.champ_nom.text(),
                    categorie=self.champ_categorie.text().strip() or None,
                    unite=self.champ_unite.currentText(),
                    prix_achat=self.champ_prix_achat.value(),
                    prix_vente=self.champ_prix_vente.value(),
                    seuil_alerte=self.champ_seuil_alerte.value(),
                    fournisseur_id=self.champ_fournisseur.currentData(),
                )
        except ValueError as erreur:
            QMessageBox.warning(self, "Erreur de saisie", str(erreur))
            return

        self.accept()
