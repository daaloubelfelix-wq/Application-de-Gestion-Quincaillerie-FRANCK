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

pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-empaquetage.txt

pyinstaller --noconfirm --windowed --onefile --name QuincaillerieFranck main.py

echo.
echo ============================================================
echo Termine. L'executable se trouve dans : dist\QuincaillerieFranck.exe
echo.
echo Pour chaque poste : copier QuincaillerieFranck.exe ET config.ini
echo (voir config.example.ini) dans le meme dossier, puis lancer le .exe.
echo ============================================================
pause
