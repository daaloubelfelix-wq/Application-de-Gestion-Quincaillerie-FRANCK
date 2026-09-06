"""
Ouverture et impression de fichiers (les tickets/factures PDF), avec le
comportement natif de chaque système d'exploitation.
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


def imprimer_fichier(chemin):
    """
    Envoie le fichier à l'imprimante par défaut. Sous Windows, utilise le
    verbe "print" associé au PDF (généralement le lecteur PDF installé) ;
    sous Mac/Linux, la commande d'impression du système.
    """
    if sys.platform.startswith("win"):
        import os
        os.startfile(chemin, "print")
    elif sys.platform == "darwin":
        subprocess.run(["lpr", chemin], check=False)
    else:
        subprocess.run(["lp", chemin], check=False)
