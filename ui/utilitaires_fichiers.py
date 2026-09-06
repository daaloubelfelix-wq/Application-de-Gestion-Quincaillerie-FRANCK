"""
Ouverture de fichiers (les tickets/factures PDF) avec le lecteur par
défaut du système, pour que l'utilisateur voie toujours un aperçu avant
d'imprimer — pas d'impression silencieuse directe.
"""

import subprocess
import sys


def ouvrir_fichier(chemin):
    if sys.platform.startswith("win"):
        import os
        os.startfile(chemin)
    elif sys.platform == "darwin":
        subprocess.run(["open", chemin], check=False)
    else:
        subprocess.run(["xdg-open", chemin], check=False)
