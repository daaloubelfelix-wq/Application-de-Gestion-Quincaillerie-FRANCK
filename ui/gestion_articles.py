"""
Écran de gestion des articles.
Liste filtrable par catégorie/recherche, alertes visuelles de stock faible,
ajout et modification via formulaire. Le responsable (site_id = None) voit
et gère les articles de tous les sites, avec une colonne Site en plus ;
un agent stock ne voit que les articles de son propre site.
"""

from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QComboBox, QHeaderView, QFileDialog,
    QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from modules.articles import lister_articles
from modules.export_excel import exporter_articles_excel
from ui.formulaire_article import FormulaireArticle


class GestionArticles(QWidget):
    def __init__(self, utilisateur):
        super().__init__()
        self.utilisateur = utilisateur
        self.tous_les_sites = utilisateur["site_id"] is None
        # L'agent stock gère l'inventaire (nom, quantité, seuil), pas les
        # montants — réservés au responsable, voir ui/formulaire_article.py.
        self.affiche_prix = utilisateur["role"] == "responsable"
        self._construire_interface()
        self._rafraichir_liste()

    def _construire_interface(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        entete = QHBoxLayout()
        nom_perimetre = self.utilisateur["site_nom"] or "Tous les sites"
        titre = QLabel(f"Articles · {nom_perimetre}")
        titre.setStyleSheet("font-size: 15px; font-weight: bold;")
        bouton_exporter = QPushButton("Exporter Excel")
        bouton_exporter.setProperty("secondaire", True)
        bouton_exporter.clicked.connect(self._exporter_excel)

        bouton_ajouter = QPushButton("+ Ajouter un article")
        bouton_ajouter.clicked.connect(self._ouvrir_formulaire_ajout)
        entete.addWidget(titre)
        entete.addStretch()
        entete.addWidget(bouton_exporter)
        entete.addWidget(bouton_ajouter)
        layout.addLayout(entete)

        filtres = QHBoxLayout()
        self.champ_recherche = QLineEdit()
        self.champ_recherche.setPlaceholderText("Rechercher un article...")
        self.champ_recherche.textChanged.connect(self._rafraichir_liste)
        filtres.addWidget(self.champ_recherche)
        layout.addLayout(filtres)

        self.colonnes = ["Nom"]
        if self.tous_les_sites:
            self.colonnes.append("Site")
        if self.affiche_prix:
            self.colonnes.append("Prix de vente")
        self.colonnes += ["Stock", "Seuil", "Action"]

        self.tableau = QTableWidget()
        self.tableau.setColumnCount(len(self.colonnes))
        self.tableau.setHorizontalHeaderLabels(self.colonnes)
        self.tableau.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.tableau.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tableau.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.tableau)

        self.setLayout(layout)

    def _rafraichir_liste(self):
        articles = lister_articles(
            site_id=self.utilisateur["site_id"],
            terme_recherche=self.champ_recherche.text().strip() or None,
        )

        self.tableau.setRowCount(len(articles))
        for ligne, article in enumerate(articles):
            colonne = 0
            self.tableau.setItem(ligne, colonne, QTableWidgetItem(article["nom"]))
            colonne += 1
            if self.tous_les_sites:
                self.tableau.setItem(ligne, colonne, QTableWidgetItem(article["site_nom"]))
                colonne += 1
            if self.affiche_prix:
                self.tableau.setItem(ligne, colonne, QTableWidgetItem(f"{article['prix_vente']:.0f} FCFA"))
                colonne += 1

            item_stock = QTableWidgetItem(str(article["quantite_stock"]))
            if article["quantite_stock"] <= article["seuil_alerte"]:
                item_stock.setBackground(QColor("#F0DDD0"))
                item_stock.setForeground(QColor("#9C3D1F"))
            self.tableau.setItem(ligne, colonne, item_stock)
            colonne += 1

            self.tableau.setItem(ligne, colonne, QTableWidgetItem(str(article["seuil_alerte"])))
            colonne += 1

            bouton_modifier = QPushButton("Modifier")
            bouton_modifier.clicked.connect(
                lambda _, a=article: self._ouvrir_formulaire_modification(a)
            )
            self.tableau.setCellWidget(ligne, colonne, bouton_modifier)

    def _ouvrir_formulaire_ajout(self):
        dialogue = FormulaireArticle(self.utilisateur, article=None, parent=self)
        if dialogue.exec():
            self._rafraichir_liste()

    def _ouvrir_formulaire_modification(self, article):
        dialogue = FormulaireArticle(self.utilisateur, article=article, parent=self)
        if dialogue.exec():
            self._rafraichir_liste()

    def _exporter_excel(self):
        articles = lister_articles(
            site_id=self.utilisateur["site_id"],
            terme_recherche=self.champ_recherche.text().strip() or None,
        )
        nom_perimetre = self.utilisateur["site_nom"] or "Tous les sites"
        nom_suggere = f"Stock {nom_perimetre} - {datetime.now().strftime('%Y-%m-%d')}.xlsx"
        chemin, _ = QFileDialog.getSaveFileName(
            self, "Exporter le stock en Excel", nom_suggere, "Classeur Excel (*.xlsx)"
        )
        if not chemin:
            return

        try:
            exporter_articles_excel(chemin, articles, inclure_prix=self.affiche_prix)
        except OSError as erreur:
            QMessageBox.warning(self, "Export impossible", str(erreur))
            return
        QMessageBox.information(self, "Export réussi", f"Le fichier a été enregistré :\n{chemin}")
