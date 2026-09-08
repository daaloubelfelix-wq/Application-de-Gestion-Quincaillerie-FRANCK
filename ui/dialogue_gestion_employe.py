"""
Fiche détaillée d'un employé : solde des avances non remboursées,
et historique des absences/congés/avances — avec les deux actions
rapides pour en enregistrer de nouvelles.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView
)

from modules.rh import lister_absences_conges, lister_avances, solde_avances_non_remboursees
from ui.dialogue_absence_conge import DialogueAbsenceConge
from ui.dialogue_avance_salaire import DialogueAvanceSalaire

_LIBELLES_TYPE = {"absence": "Absence", "conge": "Congé"}


class DialogueGestionEmploye(QDialog):
    def __init__(self, employe, utilisateur, parent=None):
        super().__init__(parent)
        self.employe = employe
        self.utilisateur = utilisateur
        self.setWindowTitle(f"Fiche employé — {employe['nom_complet']}")
        self.setMinimumSize(480, 420)
        self._construire_interface()
        self._rafraichir()

    def _construire_interface(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        titre = QLabel(f"{self.employe['nom_complet']} — {self.employe.get('poste') or 'Poste non précisé'}")
        titre.setObjectName("titreEcran")
        layout.addWidget(titre)

        self.label_salaire = QLabel()
        self.label_salaire.setObjectName("texteAttenue")
        layout.addWidget(self.label_salaire)

        self.label_solde_avances = QLabel()
        self.label_solde_avances.setObjectName("texteAttenue")
        layout.addWidget(self.label_solde_avances)

        actions = QHBoxLayout()
        bouton_absence = QPushButton("Enregistrer une absence / un congé")
        bouton_absence.clicked.connect(self._ouvrir_absence_conge)
        bouton_avance = QPushButton("Enregistrer une avance sur salaire")
        bouton_avance.clicked.connect(self._ouvrir_avance)
        actions.addWidget(bouton_absence)
        actions.addWidget(bouton_avance)
        layout.addLayout(actions)

        titre_historique = QLabel("Historique")
        titre_historique.setObjectName("titreSection")
        layout.addWidget(titre_historique)

        self.tableau = QTableWidget()
        self.tableau.setColumnCount(4)
        self.tableau.setHorizontalHeaderLabels(["Type", "Détail", "Motif", "Date"])
        self.tableau.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.tableau.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.tableau.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.tableau)

        bouton_fermer = QPushButton("Fermer")
        bouton_fermer.setProperty("secondaire", True)
        bouton_fermer.clicked.connect(self.accept)
        layout.addWidget(bouton_fermer)

        self.setLayout(layout)

    def _rafraichir(self):
        self.label_salaire.setText(
            f"Salaire mensuel : {float(self.employe['salaire_mensuel']):,.0f} FCFA".replace(",", " ")
        )
        solde = solde_avances_non_remboursees(self.employe["id"])
        self.label_solde_avances.setText(
            f"Avances non remboursées en cours : {solde:,.0f} FCFA".replace(",", " ")
        )

        lignes = []
        for evenement in lister_absences_conges(self.employe["id"]):
            lignes.append((
                evenement["date_debut"],
                _LIBELLES_TYPE[evenement["type"]],
                f"Du {evenement['date_debut'].strftime('%d/%m/%Y')} au {evenement['date_fin'].strftime('%d/%m/%Y')}",
                evenement["motif"] or "—",
            ))
        for avance in lister_avances(self.employe["id"]):
            statut = "remboursée" if avance["remboursee"] else "en cours"
            lignes.append((
                avance["date_avance"].date(),
                "Avance",
                f"{float(avance['montant']):,.0f} FCFA ({statut})".replace(",", " "),
                avance["motif"] or "—",
            ))
        lignes.sort(key=lambda l: l[0], reverse=True)

        self.tableau.setRowCount(len(lignes))
        for ligne, (date_tri, type_libelle, detail, motif) in enumerate(lignes):
            self.tableau.setItem(ligne, 0, QTableWidgetItem(type_libelle))
            self.tableau.setItem(ligne, 1, QTableWidgetItem(detail))
            self.tableau.setItem(ligne, 2, QTableWidgetItem(motif))
            self.tableau.setItem(ligne, 3, QTableWidgetItem(date_tri.strftime("%d/%m/%Y")))

    def _ouvrir_absence_conge(self):
        if DialogueAbsenceConge(self.employe, self.utilisateur, parent=self).exec():
            self._rafraichir()

    def _ouvrir_avance(self):
        if DialogueAvanceSalaire(self.employe, self.utilisateur, parent=self).exec():
            self._rafraichir()
