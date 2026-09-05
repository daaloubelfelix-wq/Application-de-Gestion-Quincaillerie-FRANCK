"""
Point d'entrée de l'application Ets Quincaillerie Franck.
Lance l'écran de connexion, puis redirige vers le tableau de bord
adapté au rôle de la personne connectée.
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget

import os

from ui.login_window import LoginWindow
from ui.dashboard_agent import TableauBordAgent
from ui.dashboard_responsable import TableauBordResponsable
from ui.point_de_vente import PointDeVente
from ui.caisse import Caisse
from ui.gestion_articles import GestionArticles
from ui.comptabilite import Comptabilite
from ui.rapports import Rapports
from ui.gestion_fournisseurs import GestionFournisseurs
from ui.gestion_utilisateurs import GestionUtilisateurs


class FenetrePrincipale(QMainWindow):
    """Fenêtre principale affichée après connexion réussie.
    Le contenu des onglets s'adapte précisément au rôle de la personne connectée,
    et au circuit réel de la boutique : le magasin de stock gère les articles
    (il ne vend pas directement), la comptabilité enregistre les commandes des
    clients, et le responsable tient la caisse qui encaisse le paiement.
    - agent_stock : Tableau de bord, Articles, Fournisseurs
    - agent_comptabilite : Tableau de bord, Comptabilité, Nouvelle commande
    - responsable : Tableau de bord consolidé, Caisse, Rapports, Fournisseurs, Utilisateurs
    """

    def __init__(self, utilisateur):
        super().__init__()
        self.utilisateur = utilisateur
        self.setWindowTitle(
            f"Ets Quincaillerie Franck — {utilisateur['nom_complet']} "
            f"({utilisateur['role']})"
        )
        self.setMinimumSize(960, 640)

        onglets = QTabWidget()

        if utilisateur["role"] == "responsable":
            onglets.addTab(TableauBordResponsable(utilisateur), "Tableau de bord")
            onglets.addTab(Caisse(utilisateur), "Caisse")
            onglets.addTab(Rapports(utilisateur), "Rapports")
            onglets.addTab(GestionFournisseurs(utilisateur), "Fournisseurs")
            onglets.addTab(GestionUtilisateurs(utilisateur), "Utilisateurs")
        elif utilisateur["role"] == "agent_stock":
            onglets.addTab(TableauBordAgent(utilisateur), "Tableau de bord")
            onglets.addTab(GestionArticles(utilisateur), "Articles")
            onglets.addTab(GestionFournisseurs(utilisateur), "Fournisseurs")
        elif utilisateur["role"] == "agent_comptabilite":
            onglets.addTab(TableauBordAgent(utilisateur), "Tableau de bord")
            onglets.addTab(Comptabilite(utilisateur), "Comptabilité")
            onglets.addTab(PointDeVente(utilisateur), "Nouvelle commande")

        self.setCentralWidget(onglets)


def demarrer_application_principale(utilisateur):
    global fenetre_principale
    fenetre_principale = FenetrePrincipale(utilisateur)
    fenetre_principale.show()
    fenetre_connexion.close()


def _chemin_ressource(chemin_relatif):
    """
    Trouve un fichier fourni avec l'application (ex : la feuille de style),
    que ce soit en lançant python main.py directement, ou depuis
    l'exécutable empaqueté (voir construire_exe.bat/.sh).
    """
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, chemin_relatif)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    chemin_style = _chemin_ressource(os.path.join("ui", "style.qss"))
    if os.path.exists(chemin_style):
        with open(chemin_style, "r", encoding="utf-8") as fichier_style:
            app.setStyleSheet(fichier_style.read())

    fenetre_connexion = LoginWindow(on_login_success=demarrer_application_principale)
    fenetre_connexion.show()

    sys.exit(app.exec())
