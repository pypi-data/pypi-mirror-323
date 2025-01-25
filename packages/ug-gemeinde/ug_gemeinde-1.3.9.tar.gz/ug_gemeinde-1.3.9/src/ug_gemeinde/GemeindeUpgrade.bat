REM  GemeindeUpgrade.bat
REM
REM  Diese Datei führt ein Upgrade erst der benötigten Bibliotheken und dann der GUI durch.
REM  Mit diesem Skript soll das Upgrade der GUI vereinfacht werden. Insb. kann das Upgrade
REM  der GUI dann über einen Starter auch pre Mausklick gestartet werden.

REM  Virtuelle Umgebung aktivieren
echo "Virtuelle Umgebung aktivieren"
.\venv\Scripts\activate

REM  GUI Upgrade
REM      pip übersieht durch Caching unter Umständen neue Versionen. Dem beugen wir vor
REM      1.  durch pip cache purge
REM      2.  durch --no-cache-dir
REM  Braucht man wirklich beide Schritte?
pip cache purge
pip install --no-cache-dir -U ugbib_divers ugbib_modell ugbib_tkinter ugbib_werkzeug
pip install --no-cache-dir -U ug_gemeinde

REM  Virtuelle Umgebung deaktivieren
deactivate
