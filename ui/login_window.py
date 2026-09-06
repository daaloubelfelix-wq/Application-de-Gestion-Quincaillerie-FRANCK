"""
Écran d'accueil et de connexion.
Reprend fidèlement le modèle validé : fond papier chaud, motif d'outils
en filigrane, badge circulaire façon mallette à outils, carte de
connexion avec deux pastilles décoratives dans les coins. Le rôle et le
site sont déterminés automatiquement en base de données à partir de
l'identifiant.
"""

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QFrame
)

from modules.auth import authentifier
from ui.icones import icone_oeil, icone_boite_outils
from ui.motif_outils import MotifOutilsFond

_COULEUR_OEIL = "#6B6357"
_COULEUR_LIGNE = QColor("#D8CFB7")


class CarteConnexion(QFrame):
    """Carte de connexion avec deux petites pastilles décoratives dans
    les coins supérieurs, façon carte perforée (voir le modèle validé)."""

    def paintEvent(self, event):
        super().paintEvent(event)
        peintre = QPainter(self)
        peintre.setRenderHint(QPainter.RenderHint.Antialiasing)
        peintre.setPen(Qt.PenStyle.NoPen)
        peintre.setBrush(_COULEUR_LIGNE)
        rayon = 3.5
        peintre.drawEllipse(QPointF(13.5, 13.5), rayon, rayon)
        peintre.drawEllipse(QPointF(self.width() - 13.5, 13.5), rayon, rayon)
        peintre.end()


class LoginWindow(QWidget):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.setWindowTitle("Ets Quincaillerie Franck — Connexion")
        self.resize(480, 640)
        self.setMinimumSize(420, 560)
        self._construire_interface()

    def _construire_interface(self):
        self.setObjectName("ecranConnexion")

        self.fond = MotifOutilsFond(parent=self)
        self.fond.setGeometry(self.rect())
        self.fond.lower()

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 40, 30, 40)
        layout.addStretch()
        layout.addWidget(self._construire_plaque_enseigne(), alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addSpacing(28)
        layout.addWidget(self._construire_carte_connexion(), alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addStretch()
        self.setLayout(layout)

    def resizeEvent(self, event):
        self.fond.setGeometry(self.rect())
        super().resizeEvent(event)

    def _construire_plaque_enseigne(self):
        plaque = QWidget()
        plaque.setObjectName("plaqueEnseigne")
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        embleme = QLabel()
        embleme.setObjectName("embleme")
        embleme.setFixedSize(64, 64)
        embleme.setAlignment(Qt.AlignmentFlag.AlignCenter)
        embleme.setPixmap(icone_boite_outils(couleur="#152C4D", taille=34))

        titre = QLabel("Ets Quincaillerie\nFranck")
        titre.setObjectName("titreEnseigne")
        titre.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(embleme, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addSpacing(14)
        layout.addWidget(titre)
        plaque.setLayout(layout)
        return plaque

    def _construire_carte_connexion(self):
        carte = CarteConnexion()
        carte.setObjectName("carteConnexion")
        carte.setFixedWidth(360)
        layout = QVBoxLayout()
        layout.setContentsMargins(26, 28, 26, 24)
        layout.setSpacing(4)

        label_identifiant = QLabel("Identifiant")
        label_identifiant.setObjectName("etiquetteChamp")

        self.champ_identifiant = QLineEdit()

        label_mdp = QLabel("Mot de passe")
        label_mdp.setObjectName("etiquetteChamp")

        ligne_mot_de_passe = QHBoxLayout()
        ligne_mot_de_passe.setSpacing(6)
        self.champ_mot_de_passe = QLineEdit()
        self.champ_mot_de_passe.setEchoMode(QLineEdit.EchoMode.Password)
        self.champ_mot_de_passe.returnPressed.connect(self._tenter_connexion)

        self.bouton_oeil = QPushButton()
        self.bouton_oeil.setObjectName("boutonOeil")
        self.bouton_oeil.setCheckable(True)
        self.bouton_oeil.setIcon(icone_oeil(ouvert=False, couleur=_COULEUR_OEIL))
        self.bouton_oeil.setToolTip("Afficher le mot de passe")
        self.bouton_oeil.setFixedSize(34, 34)
        self.bouton_oeil.clicked.connect(self._basculer_visibilite_mot_de_passe)

        ligne_mot_de_passe.addWidget(self.champ_mot_de_passe)
        ligne_mot_de_passe.addWidget(self.bouton_oeil)

        bouton_connexion = QPushButton("Se connecter")
        bouton_connexion.setObjectName("boutonConnexionPrincipal")
        bouton_connexion.clicked.connect(self._tenter_connexion)

        self.label_erreur = QLabel("")
        self.label_erreur.setObjectName("messageErreurConnexion")
        self.label_erreur.setWordWrap(True)
        self.label_erreur.hide()

        aide = QLabel("Mot de passe oublié ? Veuillez contacter le responsable.")
        aide.setObjectName("texteAideConnexion")
        aide.setAlignment(Qt.AlignmentFlag.AlignCenter)
        aide.setWordWrap(True)

        layout.addWidget(label_identifiant)
        layout.addWidget(self.champ_identifiant)
        layout.addSpacing(8)
        layout.addWidget(label_mdp)
        layout.addLayout(ligne_mot_de_passe)
        layout.addSpacing(10)
        layout.addWidget(bouton_connexion)
        layout.addWidget(self.label_erreur)
        layout.addSpacing(10)
        layout.addWidget(aide)

        carte.setLayout(layout)
        return carte

    def _basculer_visibilite_mot_de_passe(self):
        visible = self.bouton_oeil.isChecked()
        self.champ_mot_de_passe.setEchoMode(
            QLineEdit.EchoMode.Normal if visible else QLineEdit.EchoMode.Password
        )
        self.bouton_oeil.setIcon(icone_oeil(ouvert=visible, couleur=_COULEUR_OEIL))
        self.bouton_oeil.setToolTip("Masquer le mot de passe" if visible else "Afficher le mot de passe")

    def _tenter_connexion(self):
        identifiant = self.champ_identifiant.text().strip()
        mot_de_passe = self.champ_mot_de_passe.text()

        if not identifiant or not mot_de_passe:
            self._afficher_erreur("Veuillez remplir l'identifiant et le mot de passe.")
            return

        try:
            utilisateur = authentifier(identifiant, mot_de_passe)
        except ConnectionError as erreur:
            QMessageBox.critical(self, "Connexion au serveur impossible", str(erreur))
            return
        except ValueError as erreur:
            self._afficher_erreur(str(erreur))
            self.champ_mot_de_passe.clear()
            return

        self.label_erreur.hide()
        self.on_login_success(utilisateur)

    def _afficher_erreur(self, message):
        self.label_erreur.setText(message)
        self.label_erreur.show()
