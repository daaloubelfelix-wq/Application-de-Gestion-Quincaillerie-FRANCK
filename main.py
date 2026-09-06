"""
Point d'entrée de l'application Ets Quincaillerie Franck.
Lance l'écran de connexion, puis redirige vers le tableau de bord
adapté au rôle de la personne connectée.
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QPushButton

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
from ui.dialogue_mot_de_passe import DialogueMotDePasse
from ui.gestion_rh import GestionRH


class FenetrePrincipale(QMainWindow):
    """Fenêtre principale affichée après connexion réussie.
    Le contenu des onglets s'adapte précisément au rôle de la personne connectée,
    et au circuit réel de la boutique : le magasin de stock gère les articles
    (il ne vend pas directement) ; le client paie d'abord directement au
    responsable à la caisse (note manuscrite sur le facturier papier) ; la
    comptabilité saisit ensuite tout dans l'ordinateur en une seule fois, ce
    qui imprime directement le reçu final (voir ui/point_de_vente.py).
    - agent_stock : Tableau de bord, Articles — gère uniquement nom/quantité/seuil,
      pas les montants ni les fournisseurs (réservés au responsable)
    - agent_comptabilite : Tableau de bord, Comptabilité, Enregistrer une vente
      — peut être rattaché au Comptoir ou au Magasin de stock selon le site
    - responsable : Tableau de bord consolidé, Articles (tous sites, seul à voir/fixer
      les prix), Historique des ventes (vérification/annulation), Rapports,
      Fournisseurs, Personnel (RH), Utilisateurs — seul le responsable peut changer
      le prix d'un article existant (voir ui/formulaire_article.py) ou annuler une
      vente déjà payée
    """

    def __init__(self, utilisateur, on_deconnexion=None):
        super().__init__()
        self.utilisateur = utilisateur
        self.on_deconnexion = on_deconnexion
        self.setWindowTitle(
            f"Ets Quincaillerie Franck — {utilisateur['nom_complet']} "
            f"({utilisateur['role']})"
        )
        self.setMinimumSize(960, 640)

        barre_haut = QHBoxLayout()
        barre_haut.setContentsMargins(12, 8, 12, 0)
        barre_haut.addStretch()
        bouton_mot_de_passe = QPushButton("Modifier mon mot de passe")
        bouton_mot_de_passe.setProperty("secondaire", True)
        bouton_mot_de_passe.clicked.connect(self._modifier_mot_de_passe)
        barre_haut.addWidget(bouton_mot_de_passe)
        bouton_deconnexion = QPushButton("Se déconnecter")
        bouton_deconnexion.setProperty("secondaire", True)
        bouton_deconnexion.clicked.connect(self._se_deconnecter)
        barre_haut.addWidget(bouton_deconnexion)

        onglets = QTabWidget()

        if utilisateur["role"] == "responsable":
            onglets.addTab(TableauBordResponsable(utilisateur), "Tableau de bord")
            onglets.addTab(GestionArticles(utilisateur), "Articles")
            onglets.addTab(Caisse(utilisateur), "Historique des ventes")
            onglets.addTab(Rapports(utilisateur), "Rapports")
            onglets.addTab(GestionFournisseurs(utilisateur), "Fournisseurs")
            onglets.addTab(GestionRH(utilisateur), "Personnel")
            onglets.addTab(GestionUtilisateurs(utilisateur), "Utilisateurs")
        elif utilisateur["role"] == "agent_stock":
            onglets.addTab(TableauBordAgent(utilisateur), "Tableau de bord")
            onglets.addTab(GestionArticles(utilisateur), "Articles")
        elif utilisateur["role"] == "agent_comptabilite":
            onglets.addTab(TableauBordAgent(utilisateur), "Tableau de bord")
            onglets.addTab(Comptabilite(utilisateur), "Comptabilité")
            onglets.addTab(PointDeVente(utilisateur), "Enregistrer une vente")

        conteneur = QWidget()
        layout_conteneur = QVBoxLayout()
        layout_conteneur.setContentsMargins(0, 0, 0, 0)
        layout_conteneur.setSpacing(0)
        layout_conteneur.addLayout(barre_haut)
        layout_conteneur.addWidget(onglets)
        conteneur.setLayout(layout_conteneur)

        self.setCentralWidget(conteneur)

    def _modifier_mot_de_passe(self):
        DialogueMotDePasse(self.utilisateur, parent=self).exec()

    def _se_deconnecter(self):
        if self.on_deconnexion:
            self.on_deconnexion()
        self.close()


def demarrer_application_principale(utilisateur):
    global fenetre_principale
    fenetre_principale = FenetrePrincipale(utilisateur, on_deconnexion=revenir_a_connexion)
    fenetre_principale.show()
    fenetre_connexion.close()


def revenir_a_connexion():
    global fenetre_connexion
    fenetre_connexion = LoginWindow(on_login_success=demarrer_application_principale)
    fenetre_connexion.show()


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
