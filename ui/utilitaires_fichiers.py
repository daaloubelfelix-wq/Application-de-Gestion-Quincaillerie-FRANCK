"""
Ouverture et impression de fichiers (les tickets/factures PDF) avec les
applications par défaut du système.
"""

import subprocess
import sys


def ouvrir_fichier(chemin):
    """Ouvre le fichier dans le lecteur par défaut (aperçu à l'écran)."""
    if sys.platform.startswith("win"):
        import os
        os.startfile(chemin)
    elif sys.platform == "darwin":
        subprocess.run(["open", chemin], check=False)
    else:
        subprocess.run(["xdg-open", chemin], check=False)


def imprimer_fichier(chemin):
    """Envoie directement le fichier à l'impression, sans passer par un
    aperçu à l'écran : sous Windows, utilise le verbe "print" du lecteur
    PDF par défaut, qui ouvre en général directement la fenêtre
    d'impression prête à confirmer (au lieu d'ouvrir le PDF puis de
    devoir cliquer sur imprimer soi-même)."""
    if sys.platform.startswith("win"):
        import os
        os.startfile(chemin, "print")
    else:
        # Pas de verbe d'impression standard hors Windows : on ouvre le
        # fichier, l'utilisateur lance l'impression depuis le lecteur.
        ouvrir_fichier(chemin)
