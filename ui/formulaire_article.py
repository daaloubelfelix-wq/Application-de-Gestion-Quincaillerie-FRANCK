"""
Formulaire d'ajout ou de modification d'un article.
Réutilisé pour la création (article=None) et la modification (article fourni).

Contrôle anti-fraude : sur un article déjà existant, seul le responsable
peut changer le prix d'achat ou de vente (l'agent stock voit les prix mais
ne peut pas les modifier) ; tout changement de prix qui a lieu est de toute
façon enregistré dans historique_prix_articles (voir modules/articles.py),
pour qu'un prix modifié laisse toujours une trace.
"""

from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QDoubleSpinBox, QSpinBox,
    QComboBox, QDialogButtonBox, QMessageBox, QLabel
)

from database import Database
from modules.articles import (
    creer_article, modifier_article, lister_fournisseurs, derniere_modification_prix,
)

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

        # Un article existant appartient déjà à un site ; à la création,
        # le responsable (qui supervise tous les sites) doit choisir lequel.
        self.champ_site = None
        if self.article is None and self.utilisateur["site_id"] is None:
            self.champ_site = QComboBox()
            for site in Database.fetch_all("SELECT id, nom FROM sites ORDER BY nom"):
                self.champ_site.addItem(site["nom"], site["id"])
            layout.addRow("Site", self.champ_site)

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
            self._appliquer_restriction_prix()
            self._afficher_derniere_modification(layout)

        boutons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        boutons.button(QDialogButtonBox.StandardButton.Save).setText("Enregistrer")
        boutons.button(QDialogButtonBox.StandardButton.Cancel).setText("Annuler")
        boutons.accepted.connect(self._valider)
        boutons.rejected.connect(self.reject)
        layout.addRow(boutons)

        self.setLayout(layout)

    def _appliquer_restriction_prix(self):
        """Sur un article existant, seul le responsable change les prix."""
        if self.utilisateur["role"] != "responsable":
            self.champ_prix_achat.setEnabled(False)
            self.champ_prix_vente.setEnabled(False)
            self.champ_prix_achat.setToolTip("Seul le responsable peut modifier les prix.")
            self.champ_prix_vente.setToolTip("Seul le responsable peut modifier les prix.")

    def _afficher_derniere_modification(self, layout):
        derniere = derniere_modification_prix(self.article["id"])
        if not derniere:
            return
        texte = (
            f"Dernier changement de prix par {derniere['nom_complet']} "
            f"le {derniere['date_modification'].strftime('%d/%m/%Y %H:%M')} : "
            f"vente {derniere['ancien_prix_vente']:.0f} → {derniere['nouveau_prix_vente']:.0f} FCFA"
        )
        label = QLabel(texte)
        label.setObjectName("texteAttenue")
        label.setWordWrap(True)
        layout.addRow(label)

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
                site_id = self.champ_site.currentData() if self.champ_site else self.utilisateur["site_id"]
                creer_article(
                    site_id=site_id,
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
                    utilisateur_id=self.utilisateur["id"],
                    fournisseur_id=self.champ_fournisseur.currentData(),
                )
        except ValueError as erreur:
            QMessageBox.warning(self, "Erreur de saisie", str(erreur))
            return

        self.accept()
