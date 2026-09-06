"""
Écran de comptage d'inventaire physique — agent stock uniquement,
matin et soir. La quantité attendue par le système n'est volontairement
PAS affichée pendant la saisie (comptage à l'aveugle, pour que ce soit
un vrai contrôle) — elle n'apparaît qu'après validation, dans le
résultat, si un écart est détecté.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QSpinBox, QMessageBox
)

from modules.articles import lister_articles
from modules.inventaire import enregistrer_comptage, MOMENTS


class ComptageStock(QDialog):
    def __init__(self, utilisateur, parent=None):
        super().__init__(parent)
        self.utilisateur = utilisateur
        self.setWindowTitle("Comptage d'inventaire")
        self.resize(480, 520)
        self._construire_interface()
        self._rafraichir_liste()

    def _construire_interface(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        titre = QLabel("Comptage d'inventaire")
        titre.setObjectName("titreEcran")
        layout.addWidget(titre)

        sous_titre = QLabel(
            "Comptez physiquement chaque article présent en rayon, matin et soir, "
            "et indiquez la quantité trouvée — sans regarder ce que dit l'ordinateur."
        )
        sous_titre.setObjectName("texteAttenue")
        sous_titre.setWordWrap(True)
        layout.addWidget(sous_titre)

        entete = QHBoxLayout()
        entete.addWidget(QLabel("Moment :"))
        self.selecteur_moment = QComboBox()
        for code, libelle in MOMENTS:
            self.selecteur_moment.addItem(libelle, code)
        entete.addWidget(self.selecteur_moment)
        entete.addStretch()
        layout.addLayout(entete)

        self.tableau = QTableWidget()
        self.tableau.setColumnCount(2)
        self.tableau.setHorizontalHeaderLabels(["Article", "Quantité comptée"])
        self.tableau.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tableau.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.tableau.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.tableau)

        bouton_valider = QPushButton("Valider le comptage")
        bouton_valider.clicked.connect(self._valider_comptage)
        layout.addWidget(bouton_valider)

        self.setLayout(layout)

    def _rafraichir_liste(self):
        self.articles = lister_articles(site_id=self.utilisateur["site_id"])
        self.tableau.setRowCount(len(self.articles))
        self.champs_quantite = []
        for ligne, article in enumerate(self.articles):
            self.tableau.setItem(ligne, 0, QTableWidgetItem(article["nom"]))
            champ = QSpinBox()
            champ.setRange(0, 1_000_000)
            self.tableau.setCellWidget(ligne, 1, champ)
            self.champs_quantite.append(champ)

    def _valider_comptage(self):
        if not self.articles:
            QMessageBox.information(self, "Aucun article", "Aucun article n'est enregistré sur ce site.")
            return

        moment = self.selecteur_moment.currentData()
        ecarts_detectes = []

        for article, champ in zip(self.articles, self.champs_quantite):
            quantite_comptee = champ.value()
            try:
                ecart = enregistrer_comptage(article["id"], moment, quantite_comptee, self.utilisateur["id"])
            except ValueError as erreur:
                QMessageBox.warning(self, "Erreur", f"{article['nom']} : {erreur}")
                return
            if ecart != 0:
                ecarts_detectes.append((article["nom"], ecart))

        if ecarts_detectes:
            detail = "\n".join(
                f"• {nom} : {'manque' if ecart < 0 else 'en trop de'} {abs(ecart)}"
                for nom, ecart in ecarts_detectes
            )
            QMessageBox.warning(
                self, "Écart détecté",
                f"Comptage enregistré, mais un écart a été détecté :\n\n{detail}"
            )
        else:
            QMessageBox.information(
                self, "Comptage enregistré", "Comptage enregistré — tout correspond, aucun écart détecté."
            )

        self._rafraichir_liste()
