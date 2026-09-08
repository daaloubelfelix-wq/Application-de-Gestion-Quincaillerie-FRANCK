#!/usr/bin/env bash
# ============================================================
# Fabrique un exécutable Mac/Linux autonome de l'application.
# À exécuter UNE SEULE FOIS, sur une machine avec Python installé,
# depuis le dossier du projet : ./construire_exe.sh
# Le résultat (dist/QuincaillerieFranck) se copie ensuite tel quel
# sur les postes concernés, sans avoir besoin d'installer Python.
# ============================================================
set -euo pipefail

python3 -m venv .venv_empaquetage
source .venv_empaquetage/bin/activate

python3 -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-empaquetage.txt

pyinstaller --noconfirm --windowed --onefile --name QuincaillerieFranck --add-data "ui/style.qss:ui" --collect-submodules reportlab.graphics.barcode main.py
pyinstaller --noconfirm --onefile --name CreerCompteResponsable creer_compte_responsable.py

echo ""
echo "============================================================"
echo "Terminé. Les exécutables se trouvent dans :"
echo "  dist/QuincaillerieFranck        (application)"
echo "  dist/CreerCompteResponsable     (à lancer UNE FOIS, pour"
echo "                                   créer le premier compte)"
echo ""
echo "Pour chaque poste : copier QuincaillerieFranck ET config.ini"
echo "(voir config.example.ini) dans le même dossier, puis le lancer."
echo "Pour un testeur à distance (sa propre base de données), voir"
echo "GUIDE_TESTEURS_A_DISTANCE.md."
echo "============================================================"
