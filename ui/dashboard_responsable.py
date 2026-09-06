"""
Tableau de bord affiché au responsable.
Vue consolidée avec sélecteur de site, ventes et dépenses des deux sites.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PyQt6.QtCore import Qt
from datetime import date

from database import Database


class TableauBordResponsable(QWidget):
    def __init__(self, utilisateur):
        super().__init__()
        self.utilisateur = utilisateur
        self.site_selectionne_id = None  # None = tous les sites
        self._construire_interface()

    def _construire_interface(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        entete = QHBoxLayout()
        infos = QVBoxLayout()
        nom = QLabel(f"Bonjour, {self.utilisateur['nom_complet']}")
        nom.setStyleSheet("font-size: 16px; font-weight: bold;")
        role = QLabel("Responsable · Tous les sites")
        role.setStyleSheet("color: #6B6357; font-size: 12px;")
        infos.addWidget(nom)
        infos.addWidget(role)
        entete.addLayout(infos)
        entete.addStretch()
        layout.addLayout(entete)

        # Sélecteur de site
        selecteur = QHBoxLayout()
        bouton_tous = QPushButton("Tous les sites")
        bouton_tous.clicked.connect(lambda: self._changer_site(None))
        selecteur.addWidget(bouton_tous)

        for site in Database.fetch_all("SELECT id, nom FROM sites ORDER BY nom"):
            bouton_site = QPushButton(site["nom"])
            bouton_site.clicked.connect(lambda _, sid=site["id"]: self._changer_site(sid))
            selecteur.addWidget(bouton_site)
        layout.addLayout(selecteur)

        # Zone de statistiques (reconstruite à chaque changement de site)
        self.zone_stats = QVBoxLayout()
        layout.addLayout(self.zone_stats)
        self._rafraichir_stats()

        # Actions
        actions = QHBoxLayout()
        bouton_utilisateurs = QPushButton("Utilisateurs")
        bouton_rapports = QPushButton("Rapports")
        actions.addWidget(bouton_utilisateurs)
        actions.addWidget(bouton_rapports)
        layout.addLayout(actions)

        layout.addStretch()
        self.setLayout(layout)

    def _changer_site(self, site_id):
        self.site_selectionne_id = site_id
        self._rafraichir_stats()

    def _vider_zone_stats(self):
        while self.zone_stats.count():
            item = self.zone_stats.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._vider_layout(item.layout())

    def _vider_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _rafraichir_stats(self):
        # Vide la zone avant de la reconstruire — y compris les cartes
        # imbriquées dans la sous-disposition "cartes" (sinon l'ancienne
        # affichage reste figé par-dessus, comme si les boutons ne
        # faisaient rien).
        self._vider_zone_stats()

        aujourd_hui = date.today()

        condition_site = ""
        params = [aujourd_hui]
        if self.site_selectionne_id is not None:
            condition_site = "AND site_id = %s"
            params.append(self.site_selectionne_id)

        ventes_jour = Database.fetch_one(
            f"""
            SELECT COALESCE(SUM(montant), 0) AS total
            FROM transactions
            WHERE type = 'recette' AND date_transaction::date = %s {condition_site}
            """,
            params,
        )
        depenses_jour = Database.fetch_one(
            f"""
            SELECT COALESCE(SUM(montant), 0) AS total
            FROM transactions
            WHERE type = 'depense' AND date_transaction::date = %s {condition_site}
            """,
            params,
        )

        cartes = QHBoxLayout()
        cartes.addWidget(self._carte_stat("Recettes du jour", f"{ventes_jour['total']:,.0f} FCFA".replace(",", " ")))
        cartes.addWidget(self._carte_stat("Dépenses du jour", f"{depenses_jour['total']:,.0f} FCFA".replace(",", " ")))
        self.zone_stats.addLayout(cartes)

    def _carte_stat(self, titre, valeur):
        cadre = QFrame()
        cadre.setStyleSheet("background-color: #E7DFC9; border-radius: 8px; padding: 12px;")
        vlayout = QVBoxLayout()
        label_titre = QLabel(titre)
        label_titre.setStyleSheet("font-size: 12px; color: #6B6357;")
        label_valeur = QLabel(valeur)
        label_valeur.setStyleSheet("font-size: 20px; font-weight: bold;")
        vlayout.addWidget(label_titre)
        vlayout.addWidget(label_valeur)
        cadre.setLayout(vlayout)
        return cadre
