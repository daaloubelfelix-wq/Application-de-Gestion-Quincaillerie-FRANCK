"""
Dialogue affiché après la génération d'un ticket ou d'une facture PDF :
propose de l'ouvrir ou de l'imprimer directement.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox
)

from ui.utilitaires_fichiers import ouvrir_fichier, imprimer_fichier


class DialogueDocumentGenere(QDialog):
    def __init__(self, titre, message, chemin_pdf, parent=None):
        super().__init__(parent)
        self.chemin_pdf = chemin_pdf
        self.setWindowTitle(titre)
        self.setMinimumWidth(360)
        self._construire_interface(message)

    def _construire_interface(self, message):
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        label_message = QLabel(message)
        label_message.setWordWrap(True)
        layout.addWidget(label_message)

        actions = QHBoxLayout()
        bouton_ouvrir = QPushButton("Ouvrir le PDF")
        bouton_ouvrir.setProperty("secondaire", True)
        bouton_ouvrir.clicked.connect(self._ouvrir)

        bouton_imprimer = QPushButton("Imprimer")
        bouton_imprimer.clicked.connect(self._imprimer)

        actions.addWidget(bouton_ouvrir)
        actions.addWidget(bouton_imprimer)
        layout.addLayout(actions)

        bouton_fermer = QPushButton("Fermer")
        bouton_fermer.setProperty("secondaire", True)
        bouton_fermer.clicked.connect(self.accept)
        layout.addWidget(bouton_fermer)

        self.setLayout(layout)

    def _ouvrir(self):
        try:
            ouvrir_fichier(self.chemin_pdf)
        except OSError as erreur:
            QMessageBox.warning(self, "Impossible d'ouvrir le fichier", str(erreur))

    def _imprimer(self):
        try:
            imprimer_fichier(self.chemin_pdf)
        except OSError as erreur:
            QMessageBox.warning(self, "Impossible d'imprimer", str(erreur))
