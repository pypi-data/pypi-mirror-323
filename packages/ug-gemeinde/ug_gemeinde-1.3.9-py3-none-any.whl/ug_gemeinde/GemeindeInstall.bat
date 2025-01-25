REM  GemeindeInstall.ps1
REM  
REM  Diese Datei wird dem User gegeben, damit er damit die Gemeinde-GUI auf einem Windows-Rechner
REM  einfach installieren kann.
REM
REM  Als Anleitung werden ihm folgende Schritte nahegelegt:
REM      1.  Ordner/Verzeichnis für die GUI anlegen.
REM      2.  Das Skript GemeindeInstall.ps1 in dieses Verzeichnis speichern.
REM      2a. U.U. muss eine Einstellung der PowerShell geändert werden. Aus Sicherheitsgründen
REM          erlaubt die PowerShell das Ausführen von Skripten nicht. Dann muss man z.B.:
REM              a) Die PowerShell als Administrator öffnen und folgenden Befehl ausführen:
REM              b)    Set-ExecutionPolicy RemoteSigned
REM              c) Dann kann man die PowerShell wieder schließen und normal öffnen.
REM              d) Im Übrigen verweisen wir hier auf die Dokumentation von Windows.
REM      3.  Das Skript in diesem Verzeichnis ausführen, d.h.
REM          entweder   a) Terminal öffnen
REM                     b) Mit cd in das neue Verzeichnis wechseln
REM                     d) Dort das Skript ausführen (GemeindeInstall.ps1)
REM          oder       a) Das Skript im Dateimanager anklicken
REM      4.  Prüfen, ob die Installation erfolgreich war: In dem Verzeichnis müssen 
REM          mindestens folgende Dateien erschienen sein:
REM               Gemeinde.yaml
REM               Icons.yaml
REM               GemeindeStart.ps1
REM               GemeindeUpgrade.ps1
REM      5.  Damit die GUI bzw. das Upgrade bequem gestartet werden kann, sollte in
REM          einem Panel oder auf dem Schreibtisch je ein Starter für GemeindeStart.sh
REM          und GemeindeUpgrade.sh eingerichtet werden. In beiden Startern sollte
REM          "Im Terminal ausführen" aktiviert werden.
REM      6.  Optional: Um den Programmstart bzw. das dann folgende Login zu erleichtern,
REM          kann in dem Skript GemeindeStart.sh die Zeile
REM               python -m ug_gemeinde.Gemeinde
REM          ersetzt werden durch
REM               python -m ug_gemeinde.Gemeinde -u username -p password
REM          Diese beiden Werte werden dann nach dem Start der GUI automatisch in die
REM          entsprechenden Felder übernommen; es braucht nur noch der Login-Button
REM          gedrückt zu werden.
REM          WARNUNG: Diese Ergänzung sollte nur erfolgen, wenn der Rechner gut
REM                   geschützt ist vor Fremdbenutzung usw., weil Username und Passwort
REM                   im Klartext gespeichert werden.

REM  Virtuelle Umgebung herstellen
echo "Virtuelle Umgebung herstellen"
python3 -m venv venv

REM  Virtuelle Umgebung aktivieren
echo "Virtuelle Umgebung aktivieren"
.\venv\Scripts\activate

REM  GUI Gemeinde installieren
echo "GUI Gemeinde installieren"
pip cache purge
pip install --no-cache-dir ug_gemeinde

REM  GUI im Setup-Modus aufrufen.
REM  Damit wird von der GUI ein Setup ausgefürhrt, dass folgendes erledigt und dann stoppt:
REM      1. Gemeinde.yaml und Icons.yaml ins aktuelle Verzeichnis kopiert
REM      2. Upgrade-Skript GemeindeUpgrade.sh ins aktuelle Verzeichnis kopiert
REM      3. Start-Skript GemeindeStart.sh ins aktuelle Verzeichnis kopiert
REM      4. Die beiden neuen Skripte ausführbar machen
echo "GUI im Setup-Modus aufrufen"
python -m ug_gemeinde.Gemeinde --setup

REM  Virtuelle Umgebung deaktivieren
deactivate
