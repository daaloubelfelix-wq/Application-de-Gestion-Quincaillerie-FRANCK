"""
Formulaire d'ajustement manuel de stock (entrée ou sortie), pour l'agent stock.
Utilisé par exemple lors d'une réception fournisseur ou d'une casse constatée.
"""

from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QComboBox, QSpinBox, QLineEdit, QDialogButtonBox, QMessageBox
)

from modules.articles import lister_articles, ajuster_stock_manuellement


class FormulaireMouvementStock(QDialog):
    def __init__(self, utilisateur, parent=None):
        super().__init__(parent)
        self.utilisateur = utilisateur
        self.setWindowTitle("Mouvement de stock")
        self.setMinimumWidth(340)
        self._construire_interface()

    def _construire_interface(self):
        layout = QFormLayout()

        self.champ_article = QComboBox()
        for article in lister_articles(self.utilisateur["site_id"]):
            self.champ_article.addItem(
                f"{article['nom']} ({article['quantite_stock']} en stock)", article["id"]
            )

        self.champ_type = QComboBox()
        self.champ_type.addItem("Entrée (réception, réapprovisionnement)", "entree")
        self.champ_type.addItem("Sortie (casse, perte, correction)", "sortie")

        self.champ_quantite = QSpinBox()
        self.champ_quantite.setMinimum(1)
        self.champ_quantite.setMaximum(1_000_000)

        self.champ_motif = QLineEdit()
        self.champ_motif.setPlaceholderText("ex : Réception commande fournisseur")

        layout.addRow("Article", self.champ_article)
        layout.addRow("Type de mouvement", self.champ_type)
        layout.addRow("Quantité", self.champ_quantite)
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
        if self.champ_article.count() == 0:
            QMessageBox.warning(self, "Aucun article", "Aucun article n'est enregistré sur ce site.")
            return

        try:
            ajuster_stock_manuellement(
                article_id=self.champ_article.currentData(),
                type_mouvement=self.champ_type.currentData(),
                quantite=self.champ_quantite.value(),
                motif=self.champ_motif.text().strip() or None,
                utilisateur_id=self.utilisateur["id"],
            )
        except ValueError as erreur:
            QMessageBox.warning(self, "Erreur de saisie", str(erreur))
            return
        self.accept()
