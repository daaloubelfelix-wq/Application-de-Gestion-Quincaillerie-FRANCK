"""
Dialogue affiché après la génération d'un ticket ou d'une facture PDF.
Bouton principal : imprime directement (envoie le fichier à l'impression,
sans étape intermédiaire). Bouton secondaire : ouvre juste l'aperçu PDF,
pour les cas où on veut vérifier avant d'imprimer.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QMessageBox
)

from ui.utilitaires_fichiers import imprimer_fichier, ouvrir_fichier


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

        bouton_imprimer = QPushButton("Imprimer")
        bouton_imprimer.setObjectName("boutonConnexionPrincipal")
        bouton_imprimer.clicked.connect(self._imprimer)
        layout.addWidget(bouton_imprimer)

        bouton_apercu = QPushButton("Voir l'aperçu (PDF)")
        bouton_apercu.setProperty("secondaire", True)
        bouton_apercu.clicked.connect(self._ouvrir_apercu)
        layout.addWidget(bouton_apercu)

        bouton_fermer = QPushButton("Fermer")
        bouton_fermer.setProperty("secondaire", True)
        bouton_fermer.clicked.connect(self.accept)
        layout.addWidget(bouton_fermer)

        self.setLayout(layout)

    def _imprimer(self):
        try:
            imprimer_fichier(self.chemin_pdf)
        except OSError as erreur:
            QMessageBox.warning(self, "Impossible d'imprimer le fichier", str(erreur))

    def _ouvrir_apercu(self):
        try:
            ouvrir_fichier(self.chemin_pdf)
        except OSError as erreur:
            QMessageBox.warning(self, "Impossible d'ouvrir le fichier", str(erreur))
