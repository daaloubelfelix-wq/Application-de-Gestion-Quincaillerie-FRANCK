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

pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-empaquetage.txt

pyinstaller --noconfirm --windowed --onefile --name QuincaillerieFranck main.py

echo ""
echo "============================================================"
echo "Terminé. L'exécutable se trouve dans : dist/QuincaillerieFranck"
echo ""
echo "Pour chaque poste : copier QuincaillerieFranck ET config.ini"
echo "(voir config.example.ini) dans le même dossier, puis le lancer."
echo "============================================================"
