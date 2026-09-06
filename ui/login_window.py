"""
Écran d'accueil et de connexion.
Grande illustration à gauche (identité de la boutique), carte de
connexion compacte dans le coin inférieur droit. L'utilisateur entre
uniquement son identifiant et son mot de passe ; le rôle et le site sont
déterminés automatiquement en base de données.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QFrame
)
from PyQt6.QtCore import Qt

from modules.auth import authentifier
from ui.icones import icone_oeil
from ui.illustration_outils import IllustrationOutils


class LoginWindow(QWidget):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.setWindowTitle("Ets Quincaillerie Franck — Connexion")
        self.resize(1000, 620)
        self.setMinimumSize(820, 560)
        self._construire_interface()

    def _construire_interface(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(IllustrationOutils(), stretch=3)

        colonne_droite = QVBoxLayout()
        colonne_droite.setContentsMargins(28, 28, 28, 28)
        colonne_droite.addStretch(2)
        colonne_droite.addWidget(self._construire_carte_connexion())
        colonne_droite.addStretch(1)

        conteneur_droite = QWidget()
        conteneur_droite.setObjectName("panneauConnexion")
        conteneur_droite.setLayout(colonne_droite)
        conteneur_droite.setMinimumWidth(320)
        layout.addWidget(conteneur_droite, stretch=2)

        self.setLayout(layout)

    def _construire_carte_connexion(self):
        carte = QFrame()
        carte.setObjectName("carteConnexionEcran")
        carte_layout = QVBoxLayout()
        carte_layout.setContentsMargins(28, 28, 28, 28)
        carte_layout.setSpacing(10)

        invite = QLabel("Connectez-vous")
        invite.setObjectName("titreEcran")

        sous_invite = QLabel("Entrez votre identifiant et votre mot de passe.")
        sous_invite.setObjectName("texteAttenue")
        sous_invite.setWordWrap(True)

        self.champ_identifiant = QLineEdit()
        self.champ_identifiant.setPlaceholderText("Identifiant")

        ligne_mot_de_passe = QHBoxLayout()
        ligne_mot_de_passe.setSpacing(6)
        self.champ_mot_de_passe = QLineEdit()
        self.champ_mot_de_passe.setPlaceholderText("Mot de passe")
        self.champ_mot_de_passe.setEchoMode(QLineEdit.EchoMode.Password)
        self.champ_mot_de_passe.returnPressed.connect(self._tenter_connexion)

        self.bouton_oeil = QPushButton()
        self.bouton_oeil.setObjectName("boutonOeil")
        self.bouton_oeil.setCheckable(True)
        self.bouton_oeil.setIcon(icone_oeil(ouvert=False))
        self.bouton_oeil.setToolTip("Afficher le mot de passe")
        self.bouton_oeil.setFixedWidth(36)
        self.bouton_oeil.clicked.connect(self._basculer_visibilite_mot_de_passe)

        ligne_mot_de_passe.addWidget(self.champ_mot_de_passe)
        ligne_mot_de_passe.addWidget(self.bouton_oeil)

        bouton_connexion = QPushButton("Se connecter")
        bouton_connexion.clicked.connect(self._tenter_connexion)

        self.label_erreur = QLabel("")
        self.label_erreur.setObjectName("texteErreur")
        self.label_erreur.setWordWrap(True)

        aide = QLabel("Mot de passe oublié ? Contactez le responsable.")
        aide.setObjectName("texteAttenue")

        carte_layout.addWidget(invite)
        carte_layout.addWidget(sous_invite)
        carte_layout.addSpacing(6)
        carte_layout.addWidget(self.champ_identifiant)
        carte_layout.addLayout(ligne_mot_de_passe)
        carte_layout.addSpacing(4)
        carte_layout.addWidget(bouton_connexion)
        carte_layout.addWidget(self.label_erreur)
        carte_layout.addSpacing(8)
        carte_layout.addWidget(aide)

        carte.setLayout(carte_layout)
        return carte

    def _basculer_visibilite_mot_de_passe(self):
        visible = self.bouton_oeil.isChecked()
        self.champ_mot_de_passe.setEchoMode(
            QLineEdit.EchoMode.Normal if visible else QLineEdit.EchoMode.Password
        )
        self.bouton_oeil.setIcon(icone_oeil(ouvert=visible))
        self.bouton_oeil.setToolTip("Masquer le mot de passe" if visible else "Afficher le mot de passe")

    def _tenter_connexion(self):
        identifiant = self.champ_identifiant.text().strip()
        mot_de_passe = self.champ_mot_de_passe.text()

        if not identifiant or not mot_de_passe:
            self.label_erreur.setText("Veuillez remplir l'identifiant et le mot de passe.")
            return

        try:
            utilisateur = authentifier(identifiant, mot_de_passe)
        except ConnectionError as erreur:
            QMessageBox.critical(self, "Connexion au serveur impossible", str(erreur))
            return
        except ValueError as erreur:
            self.label_erreur.setText(str(erreur))
            self.champ_mot_de_passe.clear()
            return

        self.label_erreur.setText("")
        self.on_login_success(utilisateur)
