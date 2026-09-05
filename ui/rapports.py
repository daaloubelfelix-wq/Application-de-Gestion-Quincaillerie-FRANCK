"""
Écran de rapports — réservé au responsable.
Filtrable par période (semaine/mois) et par site.
"""

from datetime import date, timedelta

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView
)

from database import Database
from modules.rapports import totaux_periode, produits_plus_vendus


class Rapports(QWidget):
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
        titre = QLabel("Rapports")
        titre.setStyleSheet("font-size: 15px; font-weight: bold;")

        self.selecteur_periode = QComboBox()
        self.selecteur_periode.addItems(["Cette semaine", "Ce mois-ci", "30 derniers jours"])
        self.selecteur_periode.currentTextChanged.connect(self._rafraichir)

        self.selecteur_site = QComboBox()
        self.selecteur_site.addItem("Tous les sites", None)
        for site in Database.fetch_all("SELECT id, nom FROM sites ORDER BY nom"):
            self.selecteur_site.addItem(site["nom"], site["id"])
        self.selecteur_site.currentIndexChanged.connect(self._rafraichir)

        entete.addWidget(titre)
        entete.addStretch()
        entete.addWidget(self.selecteur_site)
        entete.addWidget(self.selecteur_periode)
        layout.addLayout(entete)

        cartes = QHBoxLayout()
        self.carte_ventes = self._creer_carte("Total ventes")
        self.carte_marge = self._creer_carte("Marge estimée")
        cartes.addWidget(self.carte_ventes)
        cartes.addWidget(self.carte_marge)
        layout.addLayout(cartes)

        titre_produits = QLabel("Produits les plus vendus")
        titre_produits.setStyleSheet("font-size: 13px; font-weight: bold;")
        layout.addWidget(titre_produits)

        self.tableau = QTableWidget()
        self.tableau.setColumnCount(2)
        self.tableau.setHorizontalHeaderLabels(["Article", "Quantité vendue"])
        self.tableau.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tableau.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.tableau)

        self.setLayout(layout)

    def _creer_carte(self, titre):
        cadre = QFrame()
        cadre.setStyleSheet("background-color: #EAE5D7; border-radius: 8px; padding: 12px;")
        vlayout = QVBoxLayout()
        label_titre = QLabel(titre)
        label_titre.setStyleSheet("font-size: 12px; color: #5B6169;")
        label_valeur = QLabel("0 FCFA")
        label_valeur.setObjectName("valeur")
        label_valeur.setStyleSheet("font-size: 20px; font-weight: bold;")
        vlayout.addWidget(label_titre)
        vlayout.addWidget(label_valeur)
        cadre.setLayout(vlayout)
        return cadre

    def _plage_dates(self):
        aujourd_hui = date.today()
        choix = self.selecteur_periode.currentText()
        if choix == "Cette semaine":
            debut = aujourd_hui - timedelta(days=aujourd_hui.weekday())
        elif choix == "Ce mois-ci":
            debut = aujourd_hui.replace(day=1)
        else:  # 30 derniers jours
            debut = aujourd_hui - timedelta(days=30)
        return debut, aujourd_hui

    def _rafraichir(self):
        date_debut, date_fin = self._plage_dates()
        site_id = self.selecteur_site.currentData()

        totaux = totaux_periode(date_debut, date_fin, site_id)
        self.carte_ventes.findChild(QLabel, "valeur").setText(
            f"{totaux['total_ventes_ttc']:,.0f} FCFA".replace(",", " ")
        )
        self.carte_marge.findChild(QLabel, "valeur").setText(
            f"{totaux['marge_estimee']:,.0f} FCFA".replace(",", " ")
        )

        produits = produits_plus_vendus(date_debut, date_fin, site_id)
        self.tableau.setRowCount(len(produits))
        for ligne, produit in enumerate(produits):
            self.tableau.setItem(ligne, 0, QTableWidgetItem(produit["nom"]))
            self.tableau.setItem(ligne, 1, QTableWidgetItem(str(produit["quantite_vendue"])))
