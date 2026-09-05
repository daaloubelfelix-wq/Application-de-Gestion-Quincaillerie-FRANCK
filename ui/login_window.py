"""
Écran de connexion.
L'utilisateur entre uniquement son identifiant et son mot de passe.
Le rôle et le site sont déterminés automatiquement en base de données.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt

from modules.auth import authentifier


class LoginWindow(QWidget):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.setWindowTitle("Ets Quincaillerie Franck — Connexion")
        self.setFixedSize(340, 320)
        self._construire_interface()

    def _construire_interface(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(12)

        titre = QLabel("Ets Quincaillerie Franck")
        titre.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titre.setStyleSheet("font-size: 16px; font-weight: bold;")

        sous_titre = QLabel("Connectez-vous à votre poste")
        sous_titre.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sous_titre.setStyleSheet("color: gray; font-size: 12px;")

        self.champ_identifiant = QLineEdit()
        self.champ_identifiant.setPlaceholderText("Identifiant")

        self.champ_mot_de_passe = QLineEdit()
        self.champ_mot_de_passe.setPlaceholderText("Mot de passe")
        self.champ_mot_de_passe.setEchoMode(QLineEdit.EchoMode.Password)
        self.champ_mot_de_passe.returnPressed.connect(self._tenter_connexion)

        bouton_connexion = QPushButton("Se connecter")
        bouton_connexion.clicked.connect(self._tenter_connexion)

        self.label_erreur = QLabel("")
        self.label_erreur.setStyleSheet("color: red; font-size: 12px;")
        self.label_erreur.setWordWrap(True)
        self.label_erreur.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(titre)
        layout.addWidget(sous_titre)
        layout.addSpacing(10)
        layout.addWidget(self.champ_identifiant)
        layout.addWidget(self.champ_mot_de_passe)
        layout.addWidget(bouton_connexion)
        layout.addWidget(self.label_erreur)
        layout.addStretch()

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
