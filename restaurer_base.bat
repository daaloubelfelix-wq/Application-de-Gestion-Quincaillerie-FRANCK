@echo off
REM ============================================================
REM Restaure une sauvegarde en cas de panne/perte de la base.
REM A utiliser uniquement en cas de besoin reel -- voir
REM GUIDE_SAUVEGARDE.md, section "En cas de besoin : restaurer".
REM
REM Usage : double-cliquer, puis indiquer le chemin complet du
REM fichier .backup a restaurer quand demande.
REM ============================================================
setlocal

set PGBIN=C:\Program Files\PostgreSQL\18\bin
set DBUSER=postgres
set NOUVELLE_BASE=quincaillerie_franck_restauree

set /p FICHIER_SAUVEGARDE="Chemin complet du fichier .backup a restaurer : "

echo.
echo Cela va creer une NOUVELLE base nommee %NOUVELLE_BASE%
echo (la base actuelle n'est jamais touchee par cette operation).
echo.
set /p CONFIRMATION="Continuer ? (O/N) : "
if /i not "%CONFIRMATION%"=="O" goto fin

"%PGBIN%\createdb.exe" -h localhost -U %DBUSER% %NOUVELLE_BASE%
"%PGBIN%\pg_restore.exe" -h localhost -U %DBUSER% -d %NOUVELLE_BASE% "%FICHIER_SAUVEGARDE%"

echo.
echo Termine. Verifiez le contenu de %NOUVELLE_BASE% avant de
echo l'utiliser reellement (renseigner son nom dans config.ini
echo une fois la verification faite).

:fin
endlocal
