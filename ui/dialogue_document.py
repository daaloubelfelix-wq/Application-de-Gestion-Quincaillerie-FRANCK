"""
Dialogue affiché après la génération d'un ticket ou d'une facture PDF.
Propose un seul bouton d'action qui ouvre le document dans le lecteur PDF
par défaut : l'utilisateur voit l'aperçu et lance l'impression lui-même
depuis ce lecteur — pas d'impression silencieuse sans visualisation.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QMessageBox
)

from ui.utilitaires_fichiers import ouvrir_fichier


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

        label_aide = QLabel("Vérifiez l'aperçu dans le lecteur PDF avant de lancer l'impression.")
        label_aide.setObjectName("texteAttenue")
        label_aide.setWordWrap(True)
        layout.addWidget(label_aide)

        bouton_apercu = QPushButton("Aperçu et impression")
        bouton_apercu.clicked.connect(self._ouvrir)
        layout.addWidget(bouton_apercu)

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
