"""
Boîte de confirmation Oui/Non en français — QMessageBox.question() affiche
"Yes"/"No" par défaut (pas de traduction française chargée), on construit
donc la boîte à la main avec des boutons explicitement en français.
"""

from PyQt6.QtWidgets import QMessageBox


def confirmer(parent, titre, message):
    boite = QMessageBox(parent)
    boite.setWindowTitle(titre)
    boite.setText(message)
    boite.setIcon(QMessageBox.Icon.Question)

    bouton_oui = boite.addButton("Oui", QMessageBox.ButtonRole.YesRole)
    bouton_non = boite.addButton("Non", QMessageBox.ButtonRole.NoRole)
    boite.setDefaultButton(bouton_non)  # sécurité : la touche Entrée ne valide pas l'action
    boite.exec()

    return boite.clickedButton() is bouton_oui
