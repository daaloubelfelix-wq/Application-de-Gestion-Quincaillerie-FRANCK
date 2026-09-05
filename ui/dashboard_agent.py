"""
Tableau de bord affiché aux agents (stock ou comptabilité).
Vue restreinte à leur site et leur module, conformément à la maquette validée.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PyQt6.QtCore import Qt

from database import Database


class TableauBordAgent(QWidget):
    def __init__(self, utilisateur):
        super().__init__()
        self.utilisateur = utilisateur
        self._construire_interface()

    def _construire_interface(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # En-tête
        entete = QHBoxLayout()
        infos = QVBoxLayout()
        nom = QLabel(f"Bonjour, {self.utilisateur['nom_complet']}")
        nom.setStyleSheet("font-size: 16px; font-weight: bold;")
        site_role = QLabel(
            f"{self.utilisateur['site_nom']} · "
            f"{'Agent stock' if self.utilisateur['role'] == 'agent_stock' else 'Agent comptabilité'}"
        )
        site_role.setStyleSheet("color: gray; font-size: 12px;")
        infos.addWidget(nom)
        infos.addWidget(site_role)
        entete.addLayout(infos)
        entete.addStretch()
        layout.addLayout(entete)

        # Cartes de statistiques
        cartes = QHBoxLayout()
        cartes.addWidget(self._carte_stat("Articles en stock", self._compter_articles()))
        cartes.addWidget(self._carte_stat("Seuils atteints", self._compter_alertes(), alerte=True))
        layout.addLayout(cartes)

        # Liste des alertes stock faible
        titre_alertes = QLabel("Alertes stock faible")
        titre_alertes.setStyleSheet("font-size: 13px; font-weight: bold;")
        layout.addWidget(titre_alertes)

        liste_alertes = self._construire_liste_alertes()
        layout.addWidget(liste_alertes)

        # Boutons d'action
        actions = QHBoxLayout()
        bouton_ajout = QPushButton("Ajouter article")
        bouton_mouvement = QPushButton("Mouvement stock")
        actions.addWidget(bouton_ajout)
        actions.addWidget(bouton_mouvement)
        layout.addLayout(actions)

        layout.addStretch()
        self.setLayout(layout)

    def _carte_stat(self, titre, valeur, alerte=False):
        cadre = QFrame()
        cadre.setStyleSheet(
            f"background-color: {'#FFF3E0' if alerte else '#F1EFE8'}; "
            "border-radius: 8px; padding: 12px;"
        )
        vlayout = QVBoxLayout()
        label_titre = QLabel(titre)
        label_titre.setStyleSheet("font-size: 12px; color: gray;")
        label_valeur = QLabel(str(valeur))
        label_valeur.setStyleSheet("font-size: 22px; font-weight: bold;")
        vlayout.addWidget(label_titre)
        vlayout.addWidget(label_valeur)
        cadre.setLayout(vlayout)
        return cadre

    def _construire_liste_alertes(self):
        cadre = QFrame()
        cadre.setStyleSheet("border: 1px solid #D3D1C7; border-radius: 8px;")
        vlayout = QVBoxLayout()
        vlayout.setSpacing(0)

        articles_alerte = Database.fetch_all(
            """
            SELECT nom, quantite_stock
            FROM articles
            WHERE site_id = %s AND quantite_stock <= seuil_alerte
            ORDER BY quantite_stock ASC
            """,
            (self.utilisateur["site_id"],),
        )

        if not articles_alerte:
            label_vide = QLabel("Aucune alerte de stock pour le moment.")
            label_vide.setStyleSheet("padding: 10px; color: gray; font-size: 13px;")
            vlayout.addWidget(label_vide)
        else:
            for article in articles_alerte:
                ligne = QHBoxLayout()
                ligne.addWidget(QLabel(article["nom"]))
                quantite_label = QLabel(f"{article['quantite_stock']} restants")
                quantite_label.setStyleSheet("color: #A32D2D;")
                quantite_label.setAlignment(Qt.AlignmentFlag.AlignRight)
                ligne.addWidget(quantite_label)
                conteneur_ligne = QWidget()
                conteneur_ligne.setLayout(ligne)
                conteneur_ligne.setStyleSheet("padding: 8px;")
                vlayout.addWidget(conteneur_ligne)

        cadre.setLayout(vlayout)
        return cadre

    def _compter_articles(self):
        resultat = Database.fetch_one(
            "SELECT COUNT(*) AS total FROM articles WHERE site_id = %s",
            (self.utilisateur["site_id"],),
        )
        return resultat["total"] if resultat else 0

    def _compter_alertes(self):
        resultat = Database.fetch_one(
            "SELECT COUNT(*) AS total FROM articles WHERE site_id = %s AND quantite_stock <= seuil_alerte",
            (self.utilisateur["site_id"],),
        )
        return resultat["total"] if resultat else 0
