REM  GemeindeStart.bat
REM
REM  Mit diesem Skript soll der Programmstart der GUI vereinfacht werden. Insb. kann die GUI
REM  dann über einen Starter auch pre Mausklick gestartet werden.

REM  Virtuelle Umgebung aktivieren
echo "Virtuelle Umgebung aktivieren"
.\venv\Scripts\activate

REM  GUI Gemeinde starten
python -m ug_gemeinde.Gemeinde
REM  alternativ:
REM python -m -ug_gemeinde.Gemeinde -u username -p password

REM  Virtuelle Umgebung deaktivieren
echo "Virtuelle Umgebung deaktivieren"
deactivate
