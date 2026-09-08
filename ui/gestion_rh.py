"""
Écran Ressources humaines — réservé au responsable.
Fiche des employés (nom, poste, salaire) ; pour les absences/congés et
les avances sur salaire, voir la fiche détaillée de chaque employé
(bouton "Gérer").
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView
)

from modules.rh import lister_employes, TYPES_CONTRAT

_LIBELLES_CONTRAT = dict(TYPES_CONTRAT)
from ui.formulaire_employe import FormulaireEmploye
from ui.dialogue_gestion_employe import DialogueGestionEmploye


class GestionRH(QWidget):
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
        titre = QLabel("Ressources humaines")
        titre.setObjectName("titreEcran")
        bouton_ajouter = QPushButton("+ Ajouter un employé")
        bouton_ajouter.clicked.connect(self._ouvrir_formulaire_ajout)
        entete.addWidget(titre)
        entete.addStretch()
        entete.addWidget(bouton_ajouter)
        layout.addLayout(entete)

        sous_titre = QLabel(
            "Fiche employé, absences/congés et avances sur salaire. Le paiement du "
            "salaire s'enregistre comme une dépense (onglet Comptabilité), en choisissant "
            "l'employé dans la liste — pour une vraie traçabilité."
        )
        sous_titre.setObjectName("texteAttenue")
        sous_titre.setWordWrap(True)
        layout.addWidget(sous_titre)

        self.tableau = QTableWidget()
        self.tableau.setColumnCount(7)
        self.tableau.setHorizontalHeaderLabels(
            ["Nom", "Poste", "Contrat", "Site", "Salaire mensuel", "Actif", "Action"]
        )
        self.tableau.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.tableau.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tableau.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.tableau)

        self.setLayout(layout)

    def _rafraichir_liste(self):
        employes = lister_employes()
        self.tableau.setRowCount(len(employes))
        for ligne, employe in enumerate(employes):
            self.tableau.setItem(ligne, 0, QTableWidgetItem(employe["nom_complet"]))
            self.tableau.setItem(ligne, 1, QTableWidgetItem(employe.get("poste") or "—"))
            self.tableau.setItem(
                ligne, 2, QTableWidgetItem(_LIBELLES_CONTRAT.get(employe.get("type_contrat"), "—"))
            )
            self.tableau.setItem(ligne, 3, QTableWidgetItem(employe.get("site_nom") or "—"))
            self.tableau.setItem(
                ligne, 4,
                QTableWidgetItem(f"{float(employe['salaire_mensuel']):,.0f} FCFA".replace(",", " ")),
            )
            self.tableau.setItem(ligne, 5, QTableWidgetItem("Oui" if employe["actif"] else "Non"))

            conteneur = QWidget()
            actions = QHBoxLayout()
            actions.setContentsMargins(0, 0, 0, 0)
            bouton_gerer = QPushButton("Gérer")
            bouton_gerer.clicked.connect(lambda _, e=employe: self._ouvrir_gestion(e))
            bouton_modifier = QPushButton("Modifier")
            bouton_modifier.setProperty("secondaire", True)
            bouton_modifier.clicked.connect(lambda _, e=employe: self._ouvrir_formulaire_modification(e))
            actions.addWidget(bouton_gerer)
            actions.addWidget(bouton_modifier)
            conteneur.setLayout(actions)
            self.tableau.setCellWidget(ligne, 6, conteneur)

    def _ouvrir_formulaire_ajout(self):
        if FormulaireEmploye(employe=None, parent=self).exec():
            self._rafraichir_liste()

    def _ouvrir_formulaire_modification(self, employe):
        if FormulaireEmploye(employe=employe, parent=self).exec():
            self._rafraichir_liste()

    def _ouvrir_gestion(self, employe):
        DialogueGestionEmploye(employe, self.utilisateur, parent=self).exec()
        self._rafraichir_liste()
