from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel,
    QListWidget, QListWidgetItem
)

from modules.fournisseurs import lister_fournisseurs, articles_fournis
from ui.formulaire_fournisseur import FormulaireFournisseur


class GestionFournisseurs(QWidget):
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
        titre = QLabel("Fournisseurs")
        titre.setStyleSheet("font-size: 15px; font-weight: bold;")
        bouton_ajouter = QPushButton("+ Ajouter")
        bouton_ajouter.clicked.connect(self._ouvrir_formulaire_ajout)
        entete.addWidget(titre)
        entete.addStretch()
        entete.addWidget(bouton_ajouter)
        layout.addLayout(entete)

        self.champ_recherche = QLineEdit()
        self.champ_recherche.setPlaceholderText("Rechercher un fournisseur...")
        self.champ_recherche.textChanged.connect(self._rafraichir)
        layout.addWidget(self.champ_recherche)

        self.liste = QListWidget()
        self.liste.itemDoubleClicked.connect(self._ouvrir_formulaire_modification)
        layout.addWidget(self.liste)

        self.setLayout(layout)

    def _rafraichir(self):
        self.liste.clear()
        for fournisseur in lister_fournisseurs(self.champ_recherche.text().strip() or None):
            articles = articles_fournis(fournisseur["id"])
            noms_categories = ", ".join(sorted({a["categorie"] or a["nom"] for a in articles})) or "aucun article lié"
            texte = (
                f"{fournisseur['nom']}\n"
                f"   {fournisseur.get('telephone') or 'pas de téléphone'} · Fournit : {noms_categories}"
            )
            item = QListWidgetItem(texte)
            item.setData(1000, fournisseur)
            self.liste.addItem(item)

    def _ouvrir_formulaire_ajout(self):
        dialogue = FormulaireFournisseur(fournisseur=None, parent=self)
        if dialogue.exec():
            self._rafraichir()

    def _ouvrir_formulaire_modification(self, item):
        fournisseur = item.data(1000)
        dialogue = FormulaireFournisseur(fournisseur=fournisseur, parent=self)
        if dialogue.exec():
            self._rafraichir()
