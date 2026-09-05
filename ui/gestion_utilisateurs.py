from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)

from modules.utilisateurs import lister_utilisateurs, activer_desactiver, reinitialiser_tentatives
from ui.formulaire_utilisateur import FormulaireUtilisateur


class GestionUtilisateurs(QWidget):
    def __init__(self, utilisateur_connecte):
        super().__init__()
        self.utilisateur_connecte = utilisateur_connecte
        self._construire_interface()
        self._rafraichir()

    def _construire_interface(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        entete = QHBoxLayout()
        titre = QLabel("Utilisateurs")
        titre.setStyleSheet("font-size: 15px; font-weight: bold;")
        bouton_creer = QPushButton("+ Créer un compte")
        bouton_creer.clicked.connect(self._ouvrir_formulaire)
        entete.addWidget(titre)
        entete.addStretch()
        entete.addWidget(bouton_creer)
        layout.addLayout(entete)

        self.tableau = QTableWidget()
        self.tableau.setColumnCount(5)
        self.tableau.setHorizontalHeaderLabels(["Nom", "Rôle", "Site", "Statut", "Action"])
        self.tableau.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.tableau.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tableau.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.tableau)

        self.setLayout(layout)

    def _rafraichir(self):
        utilisateurs = lister_utilisateurs()
        self.tableau.setRowCount(len(utilisateurs))

        libelles_roles = {
            "responsable": "Responsable",
            "agent_stock": "Agent stock",
            "agent_comptabilite": "Agent comptabilité",
        }

        for ligne, u in enumerate(utilisateurs):
            self.tableau.setItem(ligne, 0, QTableWidgetItem(u["nom_complet"]))
            self.tableau.setItem(ligne, 1, QTableWidgetItem(libelles_roles.get(u["role"], u["role"])))
            self.tableau.setItem(ligne, 2, QTableWidgetItem(u["site_nom"] or "Tous les sites"))
            self.tableau.setItem(ligne, 3, QTableWidgetItem("Actif" if u["actif"] else "Désactivé"))

            bouton = QPushButton("Désactiver" if u["actif"] else "Activer")
            bouton.clicked.connect(lambda _, uid=u["id"], actif=u["actif"]: self._basculer_statut(uid, actif))
            self.tableau.setCellWidget(ligne, 4, bouton)

    def _basculer_statut(self, utilisateur_id, actif_actuel):
        if utilisateur_id == self.utilisateur_connecte["id"]:
            QMessageBox.warning(self, "Action impossible", "Vous ne pouvez pas désactiver votre propre compte.")
            return

        if actif_actuel:
            reponse = QMessageBox.question(
                self,
                "Confirmer la désactivation",
                "Ce compte ne pourra plus se connecter tant qu'il n'aura pas été réactivé. Continuer ?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reponse != QMessageBox.StandardButton.Yes:
                return

        activer_desactiver(utilisateur_id, not actif_actuel)
        if not actif_actuel:
            reinitialiser_tentatives(utilisateur_id)
        self._rafraichir()

    def _ouvrir_formulaire(self):
        dialogue = FormulaireUtilisateur(parent=self)
        if dialogue.exec():
            self._rafraichir()
