"""
Point d'entrée de l'application Ets Quincaillerie Franck.
Lance l'écran de connexion, puis redirige vers le tableau de bord
adapté au rôle de la personne connectée.
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget

from ui.login_window import LoginWindow
from ui.dashboard_agent import TableauBordAgent
from ui.dashboard_responsable import TableauBordResponsable
from ui.point_de_vente import PointDeVente
from ui.gestion_articles import GestionArticles
from ui.comptabilite import Comptabilite
from ui.rapports import Rapports
from ui.gestion_fournisseurs import GestionFournisseurs
from ui.gestion_utilisateurs import GestionUtilisateurs


class FenetrePrincipale(QMainWindow):
    """Fenêtre principale affichée après connexion réussie.
    Le contenu des onglets s'adapte précisément au rôle de la personne connectée :
    - agent_stock : Tableau de bord, Articles, Point de vente
    - agent_comptabilite : Tableau de bord, Comptabilité, Point de vente
    - responsable : Tableau de bord consolidé (les vues détaillées par site
      seront ajoutées avec les rapports et la gestion des utilisateurs)
    """

    def __init__(self, utilisateur):
        super().__init__()
        self.utilisateur = utilisateur
        self.setWindowTitle(
            f"Ets Quincaillerie Franck — {utilisateur['nom_complet']} "
            f"({utilisateur['role']})"
        )
        self.setMinimumSize(900, 600)

        onglets = QTabWidget()

        if utilisateur["role"] == "responsable":
            onglets.addTab(TableauBordResponsable(utilisateur), "Tableau de bord")
            onglets.addTab(Rapports(utilisateur), "Rapports")
            onglets.addTab(GestionFournisseurs(utilisateur), "Fournisseurs")
            onglets.addTab(GestionUtilisateurs(utilisateur), "Utilisateurs")
        elif utilisateur["role"] == "agent_stock":
            onglets.addTab(TableauBordAgent(utilisateur), "Tableau de bord")
            onglets.addTab(GestionArticles(utilisateur), "Articles")
            onglets.addTab(GestionFournisseurs(utilisateur), "Fournisseurs")
            onglets.addTab(PointDeVente(utilisateur), "Point de vente")
        elif utilisateur["role"] == "agent_comptabilite":
            onglets.addTab(TableauBordAgent(utilisateur), "Tableau de bord")
            onglets.addTab(Comptabilite(utilisateur), "Comptabilité")
            onglets.addTab(PointDeVente(utilisateur), "Point de vente")

        self.setCentralWidget(onglets)


def demarrer_application_principale(utilisateur):
    global fenetre_principale
    fenetre_principale = FenetrePrincipale(utilisateur)
    fenetre_principale.show()
    fenetre_connexion.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    fenetre_connexion = LoginWindow(on_login_success=demarrer_application_principale)
    fenetre_connexion.show()

    sys.exit(app.exec())
