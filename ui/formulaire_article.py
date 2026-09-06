"""
Formulaire d'ajout ou de modification d'un article.
Réutilisé pour la création (article=None) et la modification (article fourni).

L'agent stock (magasin) ne s'occupe que de l'inventaire : nom, unité,
quantité, seuil d'alerte — jamais des montants ni du fournisseur, qui
restent réservés au responsable (voir ui/gestion_fournisseurs.py). Tant
que le responsable n'a pas fixé le prix de vente d'un nouvel article créé
par l'agent stock, l'article n'apparaît pas dans la recherche de vente
(voir modules/ventes.py::rechercher_articles) — pas de vente à 0 FCFA par
erreur.

Contrôle anti-fraude : sur un article déjà existant, seul le responsable
peut changer le prix de vente ; tout changement de prix est enregistré
dans historique_prix_articles. Le nom, l'unité et le seuil d'alerte sont
eux aussi tracés (historique_modifications_articles), y compris pour
l'agent stock — voir modules/articles.py — pour qu'un changement ne
passe jamais inaperçu, quel que soit le champ.
"""

from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QDoubleSpinBox, QSpinBox,
    QComboBox, QDialogButtonBox, QMessageBox, QLabel
)

from database import Database
from modules.articles import (
    creer_article, modifier_article, derniere_modification_prix, derniere_modification_champ,
)

UNITES_DISPONIBLES = ["sac", "barre", "unité", "m3", "litre", "kg", "rouleau", "bidon"]

# Suggestion de seuil d'alerte = une fraction de la quantité de départ,
# au lieu d'une valeur fixe identique pour tous les articles. Reste
# modifiable à la main si besoin — ce n'est qu'une suggestion de départ.
_FRACTION_SEUIL_SUGGERE = 0.2


class FormulaireArticle(QDialog):
    def __init__(self, utilisateur, article=None, parent=None):
        super().__init__(parent)
        self.utilisateur = utilisateur
        self.article = article  # None = création, sinon dict existant
        self.gere_les_montants = utilisateur["role"] == "responsable"
        self.setWindowTitle("Modifier l'article" if article else "Ajouter un article")
        self.setMinimumWidth(340)
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
        self.champ_unite = QComboBox()
        self.champ_unite.addItems(UNITES_DISPONIBLES)
        self.champ_unite.setEditable(True)

        self.champ_seuil_alerte = QSpinBox()
        self.champ_seuil_alerte.setMaximum(100_000)

        layout.addRow("Nom de l'article", self.champ_nom)
        layout.addRow("Unité", self.champ_unite)

        # Le prix de vente reste réservé au responsable — l'agent stock ne
        # gère que l'inventaire (nom, quantité, seuil), jamais les montants.
        self.champ_prix_vente = None
        if self.gere_les_montants:
            self.champ_prix_vente = QDoubleSpinBox()
            self.champ_prix_vente.setMaximum(100_000_000)
            self.champ_prix_vente.setSuffix(" FCFA")
            layout.addRow("Prix de vente", self.champ_prix_vente)

        layout.addRow("Seuil d'alerte", self.champ_seuil_alerte)

        if self.article is None:
            self._seuil_modifie_a_la_main = False
            self.champ_seuil_alerte.valueChanged.connect(self._sur_modification_seuil)
            self.champ_quantite_initiale = QSpinBox()
            self.champ_quantite_initiale.setMaximum(1_000_000)
            self.champ_quantite_initiale.valueChanged.connect(self._suggerer_seuil)
            layout.addRow("Quantité initiale", self.champ_quantite_initiale)
            if not self.gere_les_montants:
                note = QLabel(
                    "Le prix de vente sera fixé par le responsable — l'article "
                    "n'apparaîtra en vente qu'une fois son prix défini."
                )
                note.setObjectName("texteAttenue")
                note.setWordWrap(True)
                layout.addRow(note)
        else:
            self._pre_remplir()
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

    def _sur_modification_seuil(self, _valeur):
        self._seuil_modifie_a_la_main = True

    def _suggerer_seuil(self, quantite):
        """Suggestion automatique du seuil à partir de la quantité de
        départ, tant que l'utilisateur n'a pas lui-même changé le champ."""
        if self._seuil_modifie_a_la_main:
            return
        self.champ_seuil_alerte.blockSignals(True)
        self.champ_seuil_alerte.setValue(max(1, round(quantite * _FRACTION_SEUIL_SUGGERE)))
        self.champ_seuil_alerte.blockSignals(False)

    def _afficher_derniere_modification(self, layout):
        # Changement de prix : visible seulement du responsable, qui est
        # seul à pouvoir le modifier.
        if self.gere_les_montants:
            derniere_prix = derniere_modification_prix(self.article["id"])
            if derniere_prix:
                texte = (
                    f"Dernier changement de prix par {derniere_prix['nom_complet']} "
                    f"le {derniere_prix['date_modification'].strftime('%d/%m/%Y %H:%M')} : "
                    f"vente {derniere_prix['ancien_prix_vente']:.0f} → {derniere_prix['nouveau_prix_vente']:.0f} FCFA"
                )
                label = QLabel(texte)
                label.setObjectName("texteAttenue")
                label.setWordWrap(True)
                layout.addRow(label)

        # Changement de nom/unité/seuil : visible de tous, y compris
        # l'agent stock, qui gère justement ces champs.
        derniere_champ = derniere_modification_champ(self.article["id"])
        if derniere_champ:
            texte = (
                f"Dernière modification par {derniere_champ['nom_complet']} "
                f"le {derniere_champ['date_modification'].strftime('%d/%m/%Y %H:%M')} : "
                f"{derniere_champ['champ_libelle']} "
                f"{derniere_champ['ancienne_valeur']} → {derniere_champ['nouvelle_valeur']}"
            )
            label = QLabel(texte)
            label.setObjectName("texteAttenue")
            label.setWordWrap(True)
            layout.addRow(label)

    def _pre_remplir(self):
        self.champ_nom.setText(self.article["nom"])
        self.champ_unite.setCurrentText(self.article["unite"])
        if self.champ_prix_vente is not None:
            self.champ_prix_vente.setValue(float(self.article["prix_vente"]))
        self.champ_seuil_alerte.setValue(self.article["seuil_alerte"])

    def _valider(self):
        prix_vente = self.champ_prix_vente.value() if self.champ_prix_vente is not None else None
        try:
            if self.article is None:
                site_id = self.champ_site.currentData() if self.champ_site else self.utilisateur["site_id"]
                creer_article(
                    site_id=site_id,
                    nom=self.champ_nom.text(),
                    categorie=None,
                    unite=self.champ_unite.currentText(),
                    prix_achat=0,
                    prix_vente=prix_vente if prix_vente is not None else 0,
                    quantite_initiale=self.champ_quantite_initiale.value(),
                    seuil_alerte=self.champ_seuil_alerte.value(),
                    fournisseur_id=None,
                )
            else:
                modifier_article(
                    article_id=self.article["id"],
                    nom=self.champ_nom.text(),
                    categorie=self.article.get("categorie"),
                    unite=self.champ_unite.currentText(),
                    prix_achat=float(self.article.get("prix_achat") or 0),
                    prix_vente=prix_vente if prix_vente is not None else float(self.article["prix_vente"]),
                    seuil_alerte=self.champ_seuil_alerte.value(),
                    utilisateur_id=self.utilisateur["id"],
                    fournisseur_id=self.article.get("fournisseur_id"),
                )
        except ValueError as erreur:
            QMessageBox.warning(self, "Erreur de saisie", str(erreur))
            return

        self.accept()
