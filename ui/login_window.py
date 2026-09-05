"""
Écran de connexion.
L'utilisateur entre uniquement son identifiant et son mot de passe.
Le rôle et le site sont déterminés automatiquement en base de données.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt

from modules.auth import authentifier


class LoginWindow(QWidget):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.setWindowTitle("Ets Quincaillerie Franck — Connexion")
        self.setFixedSize(380, 460)
        self._construire_interface()

    def _construire_interface(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Bandeau d'en-tête
        banniere = QFrame()
        banniere.setObjectName("banniereConnexion")
        banniere.setFixedHeight(140)
        banniere_layout = QVBoxLayout()
        banniere_layout.setContentsMargins(24, 0, 24, 0)

        titre = QLabel("Ets Quincaillerie Franck")
        titre.setObjectName("titreConnexion")
        titre.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titre.setWordWrap(True)

        sous_titre = QLabel("Batouri · Gestion de quincaillerie")
        sous_titre.setObjectName("sousTitreConnexion")
        sous_titre.setAlignment(Qt.AlignmentFlag.AlignCenter)

        banniere_layout.addStretch()
        banniere_layout.addWidget(titre)
        banniere_layout.addWidget(sous_titre)
        banniere_layout.addStretch()
        banniere.setLayout(banniere_layout)

        # Carte de connexion
        carte = QFrame()
        carte.setObjectName("carteConnexionEcran")
        carte_layout = QVBoxLayout()
        carte_layout.setContentsMargins(32, 32, 32, 32)
        carte_layout.setSpacing(12)

        invite = QLabel("Connectez-vous à votre poste")
        invite.setObjectName("titreSection")

        self.champ_identifiant = QLineEdit()
        self.champ_identifiant.setPlaceholderText("Identifiant")

        self.champ_mot_de_passe = QLineEdit()
        self.champ_mot_de_passe.setPlaceholderText("Mot de passe")
        self.champ_mot_de_passe.setEchoMode(QLineEdit.EchoMode.Password)
        self.champ_mot_de_passe.returnPressed.connect(self._tenter_connexion)

        bouton_connexion = QPushButton("Se connecter")
        bouton_connexion.clicked.connect(self._tenter_connexion)

        self.label_erreur = QLabel("")
        self.label_erreur.setObjectName("texteErreur")
        self.label_erreur.setWordWrap(True)
        self.label_erreur.setAlignment(Qt.AlignmentFlag.AlignCenter)

        carte_layout.addWidget(invite)
        carte_layout.addSpacing(6)
        carte_layout.addWidget(self.champ_identifiant)
        carte_layout.addWidget(self.champ_mot_de_passe)
        carte_layout.addSpacing(6)
        carte_layout.addWidget(bouton_connexion)
        carte_layout.addWidget(self.label_erreur)
        carte_layout.addStretch()
        carte.setLayout(carte_layout)

        layout.addWidget(banniere)
        layout.addWidget(carte, stretch=1)

        self.setLayout(layout)

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
