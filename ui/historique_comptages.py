"""
Historique des comptages d'inventaire — réservé au responsable.
Sert de support aux réunions hebdomadaires/mensuelles où chacun présente
son comptage : les écarts (marchandise manquante ou en trop) ressortent
en rouge.
"""

from datetime import date, timedelta

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtGui import QColor

from database import Database
from modules.inventaire import historique_comptages, MOMENTS

_LIBELLES_MOMENT = dict(MOMENTS)


class HistoriqueComptages(QWidget):
    def __init__(self, utilisateur):
        super().__init__()
        self.utilisateur = utilisateur
        self._construire_interface()
        self._rafraichir()

    def _construire_interface(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        entete = QHBoxLayout()
        titre = QLabel("Inventaire — historique des comptages")
        titre.setObjectName("titreEcran")
        entete.addWidget(titre)
        entete.addStretch()

        self.selecteur_site = QComboBox()
        self.selecteur_site.addItem("Tous les sites", None)
        for site in Database.fetch_all("SELECT id, nom FROM sites ORDER BY nom"):
            self.selecteur_site.addItem(site["nom"], site["id"])
        self.selecteur_site.currentIndexChanged.connect(self._rafraichir)
        entete.addWidget(self.selecteur_site)

        self.selecteur_periode = QComboBox()
        self.selecteur_periode.addItems(["Cette semaine", "Ce mois-ci", "30 derniers jours"])
        self.selecteur_periode.currentTextChanged.connect(self._rafraichir)
        entete.addWidget(self.selecteur_periode)

        layout.addLayout(entete)

        sous_titre = QLabel(
            "Support pour la réunion : chacun présente son comptage — les écarts "
            "(marchandise manquante ou en trop) apparaissent en rouge."
        )
        sous_titre.setObjectName("texteAttenue")
        sous_titre.setWordWrap(True)
        layout.addWidget(sous_titre)

        self.tableau = QTableWidget()
        self.tableau.setColumnCount(7)
        self.tableau.setHorizontalHeaderLabels(
            ["Site", "Article", "Moment", "Attendu", "Compté", "Écart", "Enregistré par"]
        )
        self.tableau.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.tableau.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tableau.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.tableau)

        self.setLayout(layout)

    def _plage_dates(self):
        aujourd_hui = date.today()
        choix = self.selecteur_periode.currentText()
        if choix == "Cette semaine":
            debut = aujourd_hui - timedelta(days=aujourd_hui.weekday())
        elif choix == "Ce mois-ci":
            debut = aujourd_hui.replace(day=1)
        else:
            debut = aujourd_hui - timedelta(days=30)
        return debut, aujourd_hui

    def _rafraichir(self):
        date_debut, date_fin = self._plage_dates()
        site_id = self.selecteur_site.currentData()

        comptages = historique_comptages(site_id=site_id, date_debut=date_debut, date_fin=date_fin)
        self.tableau.setRowCount(len(comptages))
        for ligne, comptage in enumerate(comptages):
            self.tableau.setItem(ligne, 0, QTableWidgetItem(comptage["site_nom"]))
            self.tableau.setItem(ligne, 1, QTableWidgetItem(comptage["article_nom"]))
            self.tableau.setItem(ligne, 2, QTableWidgetItem(_LIBELLES_MOMENT.get(comptage["moment"], comptage["moment"])))
            self.tableau.setItem(ligne, 3, QTableWidgetItem(str(comptage["quantite_attendue"])))
            self.tableau.setItem(ligne, 4, QTableWidgetItem(str(comptage["quantite_comptee"])))

            item_ecart = QTableWidgetItem(str(comptage["ecart"]))
            if comptage["ecart"] != 0:
                item_ecart.setBackground(QColor("#F0DDD0"))
                item_ecart.setForeground(QColor("#9C3D1F"))
            self.tableau.setItem(ligne, 5, item_ecart)

            self.tableau.setItem(ligne, 6, QTableWidgetItem(comptage["enregistre_par"]))
