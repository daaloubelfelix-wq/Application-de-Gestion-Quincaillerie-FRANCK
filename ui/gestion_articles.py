"""
Écran de gestion des articles.
Liste filtrable par catégorie/recherche, alertes visuelles de stock faible,
ajout et modification via formulaire.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QComboBox, QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from modules.articles import lister_articles, lister_categories
from ui.formulaire_article import FormulaireArticle


class GestionArticles(QWidget):
    def __init__(self, utilisateur):
        super().__init__()
        self.utilisateur = utilisateur
        self._construire_interface()
        self._rafraichir_liste()

    def _construire_interface(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        entete = QHBoxLayout()
        titre = QLabel(f"Articles · {self.utilisateur['site_nom']}")
        titre.setStyleSheet("font-size: 15px; font-weight: bold;")
        bouton_ajouter = QPushButton("+ Ajouter un article")
        bouton_ajouter.clicked.connect(self._ouvrir_formulaire_ajout)
        entete.addWidget(titre)
        entete.addStretch()
        entete.addWidget(bouton_ajouter)
        layout.addLayout(entete)

        filtres = QHBoxLayout()
        self.champ_recherche = QLineEdit()
        self.champ_recherche.setPlaceholderText("Rechercher un article...")
        self.champ_recherche.textChanged.connect(self._rafraichir_liste)

        self.selecteur_categorie = QComboBox()
        self.selecteur_categorie.addItem("Tous")
        for categorie in lister_categories(self.utilisateur["site_id"]):
            self.selecteur_categorie.addItem(categorie)
        self.selecteur_categorie.currentTextChanged.connect(self._rafraichir_liste)

        filtres.addWidget(self.champ_recherche, stretch=3)
        filtres.addWidget(self.selecteur_categorie, stretch=1)
        layout.addLayout(filtres)

        self.tableau = QTableWidget()
        self.tableau.setColumnCount(6)
        self.tableau.setHorizontalHeaderLabels(
            ["Nom", "Catégorie", "Prix de vente", "Stock", "Seuil", "Action"]
        )
        self.tableau.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.tableau.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tableau.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.tableau)

        self.setLayout(layout)

    def _rafraichir_liste(self):
        articles = lister_articles(
            site_id=self.utilisateur["site_id"],
            categorie=self.selecteur_categorie.currentText(),
            terme_recherche=self.champ_recherche.text().strip() or None,
        )

        self.tableau.setRowCount(len(articles))
        for ligne, article in enumerate(articles):
            self.tableau.setItem(ligne, 0, QTableWidgetItem(article["nom"]))
            self.tableau.setItem(ligne, 1, QTableWidgetItem(article.get("categorie") or "—"))
            self.tableau.setItem(ligne, 2, QTableWidgetItem(f"{article['prix_vente']:.0f} FCFA"))

            item_stock = QTableWidgetItem(str(article["quantite_stock"]))
            if article["quantite_stock"] <= article["seuil_alerte"]:
                item_stock.setBackground(QColor("#F4DDD0"))
                item_stock.setForeground(QColor("#A8431C"))
            self.tableau.setItem(ligne, 3, item_stock)

            self.tableau.setItem(ligne, 4, QTableWidgetItem(str(article["seuil_alerte"])))

            bouton_modifier = QPushButton("Modifier")
            bouton_modifier.clicked.connect(
                lambda _, a=article: self._ouvrir_formulaire_modification(a)
            )
            self.tableau.setCellWidget(ligne, 5, bouton_modifier)

    def _ouvrir_formulaire_ajout(self):
        dialogue = FormulaireArticle(self.utilisateur, article=None, parent=self)
        if dialogue.exec():
            self._rafraichir_categories()
            self._rafraichir_liste()

    def _ouvrir_formulaire_modification(self, article):
        dialogue = FormulaireArticle(self.utilisateur, article=article, parent=self)
        if dialogue.exec():
            self._rafraichir_categories()
            self._rafraichir_liste()

    def _rafraichir_categories(self):
        categorie_actuelle = self.selecteur_categorie.currentText()
        self.selecteur_categorie.blockSignals(True)
        self.selecteur_categorie.clear()
        self.selecteur_categorie.addItem("Tous")
        for categorie in lister_categories(self.utilisateur["site_id"]):
            self.selecteur_categorie.addItem(categorie)
        index = self.selecteur_categorie.findText(categorie_actuelle)
        self.selecteur_categorie.setCurrentIndex(index if index >= 0 else 0)
        self.selecteur_categorie.blockSignals(False)
