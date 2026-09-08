@echo off
REM ============================================================
REM Sauvegarde automatique de la base de donnees.
REM A lancer une fois par jour (voir GUIDE_SAUVEGARDE.md pour la
REM programmer automatiquement avec le Planificateur de taches Windows).
REM
REM Le mot de passe PostgreSQL n'est jamais ecrit dans ce fichier : il
REM est lu depuis %APPDATA%\postgresql\pgpass.conf (voir le guide pour
REM le creer une seule fois).
REM ============================================================
setlocal

set PGBIN=C:\Program Files\PostgreSQL\18\bin
set DBNAME=quincaillerie_franck
set DBUSER=postgres
set DOSSIER_SAUVEGARDES=C:\Sauvegardes_Quincaillerie
REM Lettre de la cle USB destinee aux sauvegardes -- a adapter si besoin
REM (verifier dans "Ce PC" une fois la cle branchee).
set DOSSIER_USB=D:\Sauvegardes_Quincaillerie

if not exist "%DOSSIER_SAUVEGARDES%" mkdir "%DOSSIER_SAUVEGARDES%"

for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd_HHmm"') do set HORODATAGE=%%i
set NOM_FICHIER=quincaillerie_%HORODATAGE%.backup

echo Sauvegarde en cours...
"%PGBIN%\pg_dump.exe" -h localhost -U %DBUSER% -F c -f "%DOSSIER_SAUVEGARDES%\%NOM_FICHIER%" %DBNAME%

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ============================================================
    echo ECHEC de la sauvegarde -- verifier que PostgreSQL est demarre
    echo et que %APPDATA%\postgresql\pgpass.conf contient le bon mot de
    echo passe (voir GUIDE_SAUVEGARDE.md).
    echo ============================================================
    exit /b 1
)

echo Sauvegarde reussie : %DOSSIER_SAUVEGARDES%\%NOM_FICHIER%

REM Copie aussi sur la cle USB, si elle est branchee (lecteur present)
if exist "%DOSSIER_USB:~0,3%" (
    if not exist "%DOSSIER_USB%" mkdir "%DOSSIER_USB%"
    copy "%DOSSIER_SAUVEGARDES%\%NOM_FICHIER%" "%DOSSIER_USB%\" >nul
    echo Copie egalement sur la cle USB : %DOSSIER_USB%
) else (
    echo Cle USB non detectee (%DOSSIER_USB:~0,2%) -- pensez a la brancher de temps en temps pour y copier une sauvegarde.
)

REM Nettoyage : ne garde que les 30 derniers jours de sauvegardes locales
forfiles /p "%DOSSIER_SAUVEGARDES%" /m *.backup /d -30 /c "cmd /c del @path" 2>nul

endlocal
