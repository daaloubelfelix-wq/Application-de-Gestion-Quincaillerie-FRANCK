@echo off
REM ============================================================
REM Fabrique un executable Windows autonome de l'application.
REM A executer UNE SEULE FOIS, sur un PC avec Python installe,
REM depuis le dossier du projet (double-clic sur ce fichier).
REM Le resultat (dist\QuincaillerieFranck.exe) se copie ensuite
REM tel quel sur les 5 postes, sans avoir besoin d'installer
REM Python dessus.
REM ============================================================

python -m venv .venv_empaquetage
call .venv_empaquetage\Scripts\activate.bat

python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-empaquetage.txt

pyinstaller --noconfirm --windowed --onefile --name QuincaillerieFranck --add-data "ui\style.qss;ui" --collect-submodules reportlab.graphics.barcode main.py
pyinstaller --noconfirm --onefile --name CreerCompteResponsable creer_compte_responsable.py

echo.
echo ============================================================
echo Termine. Les executables se trouvent dans :
echo   dist\QuincaillerieFranck.exe        (application)
echo   dist\CreerCompteResponsable.exe     (a lancer UNE FOIS, pour
echo                                        creer le premier compte)
echo.
echo Pour chaque poste : copier QuincaillerieFranck.exe ET config.ini
echo (voir config.example.ini) dans le meme dossier, puis lancer le .exe.
echo Pour un testeur a distance (sa propre base de donnees), voir
echo GUIDE_TESTEURS_A_DISTANCE.md.
echo ============================================================
pause
