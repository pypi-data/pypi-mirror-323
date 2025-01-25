"""Gemeinde.py - Gemeinde Adressverwaltung GUI

    Beachte
        Alle Einstellungen werden der besseren Lesbarkeit in Gemeinde_Def.configuration definiert.
"""

from rich.pretty import pprint as print
import logging
from ugbib_werkzeug.bibWerkzeug import log_init
log_init('Gemeinde')
logger = logging.getLogger()

import os, sys
import datetime
sys.path.append('/home/ulrich/PythonHobby/bibs/bibtkinter/src/ugbib_tkinter/')

import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
import tkinter.font as tkFont
import tkinter.messagebox as dialog
import tkinter.filedialog as filedialog

from ugbib_divers.bibGlobal import glb
try:
    from bibForm import (
            TkIcons,
            Validator,
            Form, FormListe, BasisFormListe,
            NaviForm, NaviWidget, NaviListe,
            Notify, notify,
            BearbVonAm,
            DialogLogin, DialogGemeindeAuswahl,
            DialogHilfeNaviButtons,
            yScrolledFrame,
            FormListeUnterformular,
            FrameScrolledListbox, FrameScrolledListboxValueLabel,
            ComboboxValueLabel,
            )
except Exception as e:
    from ugbib_tkinter.bibForm import (
            TkIcons,
            Validator,
            Form, FormListe, BasisFormListe,
            NaviForm, NaviWidget, NaviListe,
            Notify, notify,
            BearbVonAm,
            DialogLogin, DialogGemeindeAuswahl,
            DialogHilfeNaviButtons,
            yScrolledFrame,
            FormListeUnterformular,
            FrameScrolledListbox, FrameScrolledListboxValueLabel,
            ComboboxValueLabel,
            )

from ugbib_modell.bibModell import setSearchPath

from .Gemeinde_Def import *
from .Gemeinde_Modelle import (
    Person, Familie, 
    Gruppe, GruppeSchlank, Versandart, Farbe, Anrede,
    PersonGruppeSchlank, PersonVersandartSchlank,
    FamilieGruppeSchlank, FamilieVersandartSchlank,
    Gemeinde,
    Jobs, JobsSchlank
    )
for M in [
        Person, Familie,
        Gruppe, GruppeSchlank, Versandart, Farbe, Anrede,
        PersonGruppeSchlank, PersonVersandartSchlank,
        FamilieGruppeSchlank, FamilieVersandartSchlank,
        Gemeinde,
        Jobs, JobsSchlank
        ]:
    M.Init(M)
    
MAIL_WITH_BCC_MESSAGE = """Achtung:
Die Protokoll-Mail ist angekreuzt.
D.h. es wird in jeder einzelnen verschickten
eMail der Absender im Bcc eingefügt.
Das sorgt u.U. für sehr viele Mails beim
Absender.
Sicher so weiter?
"""

class Hauptprogramm(tk.Tk):
    
    def __init__(self):
        super().__init__()
        self.style = ttk.Style()
        glb.icons = TkIcons()
        self.baueMenuBar()
        self.basics()
        self.baueLayout()
        self.baueValidatoren()
        self.baueWidgets()
        self.nbkMain.config(takefocus=False)
        self.disableMainNotebook()
        self.activateLogin()
    
    def basics(self):
        self.title('Gemeinde Adressverwaltung')
        self.bind_all('<Control-q>', self.handleQuit)
        self.style.theme_use('classic')    # Nur damit wird PanedWindows Trenner sichtbar
        #
        # Schriftgröße
        tkFont.nametofont('TkDefaultFont').configure(size=8)
        tkFont.nametofont('TkTextFont').configure(size=8)
        tkFont.nametofont('TkMenuFont').configure(size=8)
        tkFont.nametofont('TkFixedFont').configure(size=8)
        
    def handleQuit(self, event):
        """handleQuit - Beendet das Programm nach HotKey
        
            Ruft einfach nur ende auf.
        """
        self.ende()
    
    def ende(self):
        self.logout(tolerant=True)
        self.quit()
    
    def handleLogin(self):
        glb.PSQL_USER = self.varGlbUser.get()
        glb.PSQL_PASSWORD = self.varGlbPassword.get()
        if checkLogin():
            gemeindeAuswahl = [G['schema'] for G in glb.gemeinden]
            self.activateGemeinde()
            self.cmbGlbGemeinde['values'] = gemeindeAuswahl
            notify(f'Erfolgreich angemeldet als: {glb.PSQL_USER}', 'Erfolg')
            notify('Bitte Gemeinde auswählen', 'Info')
            self.cmbGlbGemeinde.event_generate('<Down>')
        else:
            notify('Login fehlgeschlagen', 'Warnung')
            self.activateLogin()
    
    def handleLogout(self):
        self.disableMainNotebook()
        self.activateLogin()
        self.logout()
    
    def handleGemeindeAusgewaehlt(self, event):
        glb.setvalue('schema', self.varGlbGemeinde.get())
        for G in glb.gemeinden:
            if G['schema'] == glb.schema:
                glb.setvalue('aktuelleGemeinde', G)
                break
        if not setSearchPath(f'{glb.aktuelleGemeinde["schema"]}, public'):
            notify(f'Auswahl der Gemeinde fehlgeschlagen. Einzelheiten s. Gemeinde.log.', 'Fehler')
        else:
            notify('Gemeinde erfolgreich ausgewählt.', 'Erfolg')
        Form.resetForms()
        self.enableMainNotebook()
    
    def activateLogin(self):
        """activateLogin - Hält den User auf den Login-Feldern
        
            Aktiviert die Login-Widgets und deaktiviert die Gemeinde-Auswahl
        """
        self.entGlbUser['state'] = tk.NORMAL
        self.entGlbUser.focus()
        self.entGlbPassword['state'] = tk.NORMAL
        self.btnGlbLogin.configure(state=tk.NORMAL)
        self.entGlbUser.focus()
        
        self.btnGlbLogout.configure(state=tk.DISABLED)
    
    def activateGemeinde(self):
        """activateGemeinde - Hält den User auf der Gemeinde-Auswahl
        
            Aktiviert die Gemeinde-Auswahl und deaktiviert die Login-Widgets
        """
        self.btnGlbLogout.configure(state=tk.NORMAL)
        self.cmbGlbGemeinde.focus()
        
        self.entGlbUser.configure(state=tk.DISABLED)
        self.entGlbPassword.config(state=tk.DISABLED)
        self.btnGlbLogin.config(state=tk.DISABLED)

    def baueMenuBar(self):
        #
        # Menu Bar anlegen und zeigen
        top = self.winfo_toplevel()
        self.mnuBar = tk.Menu(top)
        top['menu'] = self.mnuBar
        #
        # Menüs anlegen
        self.mnuDatei = tk.Menu(self.mnuBar, tearoff=0)
        self.mnuDB = tk.Menu(self.mnuDatei, tearoff=0)
        self.mnuHilfe = tk.Menu(self.mnuBar, tearoff=0)
        #
        # Menüs füllen
        #
        # Menü Bar füllen
        self.mnuBar.add_cascade(label='Datei', menu=self.mnuDatei)
        self.mnuBar.add_cascade(label='Hilfe', menu=self.mnuHilfe)
        # Menü Datei füllen
        self.mnuDatei.add_cascade(
            label='Datenbank',
            image=glb.icons.getIcon('database'),
            menu=self.mnuDB)
        self.mnuDatei.add_separator()
        self.mnuDatei.add_command(
            label='Beenden',
            accelerator='Strg-Q',
            image=glb.icons.getIcon('quit'),
            command=lambda : self.ende())
        # Menü DB (Datenbank) füllen
        # Menü Hilfe füllen
        self.mnuHilfe.add_command(
            label='Navi Buttons',
            command=lambda: DialogHilfeNaviButtons(self)
            )
    
    
    def logout(self, tolerant=False):
        """handleMnuLogout - Behandelt Menü Logout Button
        """
        # Falls DB Connector existiert, versuche zu schließen
        try:
            glb.DB.close()
            notify('Verbindung zur DB geschlossen', 'Erfolg')
            logging.info(f'Verbindung zur DB geschlossen.')
            glb.PSQL_PASSWORD = ''
        except Exception as e:
            if not tolerant:
                notify(e, 'Fehler')
                logging.info(f'Fehler beim Logout: {e}')
        # Koptzeile leeren
        self.varGlbDB.set('')
        self.varGlbUser.set('')
        self.varGlbPassword.set('')
        self.varGlbGemeinde.set('')
        glb.PSQL_PASSWORD = ''
        glb.PSQL_USER = ''
    
    def baueValidatoren(self):
      
        def invalidHoldFocus(widgetName):
            widget = self.nametowidget(widgetName)
            widget.focus_force()
            notify('Wert ungültig', 'Warnung')
        #
        # Validatoren
        self.valDate = self.register(Validator.valDate)
        self.valInt = self.register(Validator.valInt)
        #
        # Funktionen für invalidcommand
        self.invalidHoldFocus = self.register(invalidHoldFocus)
    
    def baueWidgets(self):
        #
        # Kopfzeile (Top) - Information über DB-Verbindung
        #
        # Variablen
        self.varGlbDB = tk.StringVar()
        self.varGlbUser = tk.StringVar()
        self.varGlbPassword = tk.StringVar()
        self.varGlbGemeinde = tk.StringVar()
        
        self.varGlbDB.set(glb.PSQL_DATABASE)
        # self.varGlbGemeinde.set(glb.aktuelleGemeinde['kurz_bez'])
        self.varGlbUser.set(glb.PSQL_USER)
        self.varGlbPassword.set(glb.PSQL_PASSWORD)
        #
        # User, Password, Gemeinde, Datenbank
        self.lblGlbUser = ttk.Label(self.frmTop, text='Benutzer:')
        self.lblGlbUser.pack(side=tk.LEFT)
        self.entGlbUser = ttk.Entry(
            self.frmTop,
            textvariable=self.varGlbUser)
        self.entGlbUser.pack(side=tk.LEFT)
        
        self.lblGlbPassword = ttk.Label(self.frmTop, text='Passwort:')
        self.lblGlbPassword.pack(side=tk.LEFT)
        self.entGlbPassword = ttk.Entry(
            self.frmTop,
            textvariable=self.varGlbPassword,
            show='*'
            )
        self.entGlbPassword.pack(side=tk.LEFT)
        
        self.btnGlbLogin = ttk.Button(
            self.frmTop,
            text='Login',
            image=glb.icons.getIcon('connect'),
            compound=tk.LEFT,
            command=self.handleLogin
            )
        self.btnGlbLogin.pack(side=tk.LEFT)
        
        self.btnGlbLogout = ttk.Button(
            self.frmTop,
            text='Logout',
            image=glb.icons.getIcon('disconnect'),
            compound=tk.LEFT,
            command=self.handleLogout
            )
        self.btnGlbLogout.pack(side=tk.LEFT)
        
        self.lblGlbGemeinde = ttk.Label(self.frmTop, text='Gemeinde:')
        self.lblGlbGemeinde.pack(side=tk.LEFT)
        self.cmbGlbGemeinde = ttk.Combobox(
            self.frmTop,
            textvariable=self.varGlbGemeinde,
            state='readonly',
            exportselection=0)
        self.cmbGlbGemeinde.bind('<<ComboboxSelected>>', self.handleGemeindeAusgewaehlt)
        self.cmbGlbGemeinde.pack(side=tk.LEFT)
        
        self.lblGlbDB = ttk.Label(self.frmTop, text='Datenbank:')
        self.lblGlbDB.pack(side=tk.LEFT)
        self.entGlbDB = ttk.Entry(
            self.frmTop,
            textvariable=self.varGlbDB,
            state=tk.DISABLED)
        self.entGlbDB.pack(side=tk.LEFT)
        #
        # Notify Widget in Fußbereich
        self.wdgNotify = Notify(self.frmBottom)
        self.wdgNotify.pack(expand=tk.YES, fill=tk.BOTH)
        for art in Notify.arten.keys():
            notify(f'Test: {art=}', art)
        ttk.Label(self.frmBottom, text='Platzhalter Bottom').pack()
        #
        # Personen Einzelheiten
        with Form() as form:
            glb.formPersonenEinzelheiten = form
            #
            # Frames für Navi, Formular und Unterformulare
            self.frmPersEinzelNavi = ttk.Frame(self.frmPersonenEinzelheiten)
            self.frmPersEinzelDaten = ttk.Frame(self.frmPersonenEinzelheiten)
            self.frmPersEinzelUnterformulare = ttk.Frame(self.frmPersonenEinzelheiten)
            
            self.frmPersEinzelNavi.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            ttk.Separator(self.frmPersonenEinzelheiten, orient=tk.VERTICAL).pack(
                side=tk.LEFT,
                fill=tk.BOTH,
                expand=True)
            self.frmPersEinzelDaten.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            ttk.Separator(self.frmPersonenEinzelheiten, orient=tk.VERTICAL).pack(
                side=tk.LEFT,
                fill=tk.BOTH,
                expand=True)
            self.frmPersEinzelUnterformulare.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            self.sfrPersEinzelGruppen = yScrolledFrame(self.frmPersEinzelUnterformulare)
            self.sfrPersEinzelVersand = yScrolledFrame(self.frmPersEinzelUnterformulare)
            self.frmPersEinzelGruppen = self.sfrPersEinzelGruppen.innerFrame
            self.frmPersEinzelVersand = self.sfrPersEinzelVersand.innerFrame
            ttk.Label(self.frmPersEinzelUnterformulare, text='Gruppen').pack(
                  side=tk.TOP,
                  anchor=tk.W)
            self.sfrPersEinzelGruppen.pack(side=tk.TOP, fill=tk.BOTH)
            ttk.Separator(self.frmPersEinzelUnterformulare, orient=tk.HORIZONTAL).pack(
                side=tk.TOP,
                expand=True,
                fill=tk.BOTH)
            ttk.Label(self.frmPersEinzelUnterformulare, text='Versandarten').pack(
                side=tk.TOP,
                anchor=tk.W)
            self.sfrPersEinzelVersand.pack(side=tk.TOP, fill=tk.BOTH)
            
            self.frmPersEinzelGruppen.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            self.frmPersEinzelVersand.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            #
            # Navi herstellen und einsetzen
            navi = NaviForm(self.frmPersEinzelNavi)
            form.setNavi(navi)
            navi.pack(fill=tk.BOTH, expand=True)
            #
            # Navi konfigurieren
            P = Person()
            navi.setGetterAuswahl(P.FactoryGetterAuswahl(
                'id',
                ('name', 'vorname', 'id',),
                ('name', 'vorname', 'strasse', 'ort',),
                'name, vorname'
                ))
            navi.setGetterValues(P.FactoryGetterValues())
            navi.setSaverValues(P.FactorySaverValues())
            navi.setDeleterValues(P.FactoryDeleterValues())
            navi.setGetterSelect('anrede', P.FactoryGetterChoices('anrede'))
            #
            # Unterformulare herstellen und an Navi hängen
            #
            # ... für Gruppen
            def FactoryFormPersonEinzelheitenGruppe():
                uform = Form()
                #
                # Navi herstellen und einsetzen
                unavi = NaviForm(self.frmPersEinzelGruppen, elemente=('save', 'delete'))
                uform.setNavi(unavi)
                #
                # Navi konfigurieren
                PG = PersonGruppeSchlank()
                unavi.setGetterValues(PG.FactoryGetterValues())
                unavi.setSaverValues(PG.FactorySaverValues())
                unavi.setDeleterValues(PG.FactoryDeleterValues())
                unavi.setGetterSelect(
                    'gruppe_kurz_bez',
                    PG.FactoryGetterChoices('gruppe_kurz_bez')
                    )
                #
                # Widgets
                uform.addWidget(
                    'id',
                    ttk.Entry(self.frmPersEinzelGruppen, state=tk.DISABLED, width=6),
                    'int',
                    label='ID')
                uform.addWidget(
                    'person_id',
                    ttk.Entry(self.frmPersEinzelGruppen, state=tk.DISABLED, width=6),
                    'int',
                    label='P-ID')
                uform.addWidget(
                    'gruppe_kurz_bez',
                    ttk.Combobox(self.frmPersEinzelGruppen, width=10),
                    'text',
                    label='Gruppe'
                    )
                #
                # Formular zurückgeben
                return uform
            FL = FormListeUnterformular(
                self.frmPersEinzelGruppen,
                FactoryFormPersonEinzelheitenGruppe,
                linkFeld='person_id',
                linkFeldHauptformular='id'
                )
            FL.setGetterDicts(PersonGruppeSchlank().FactoryGetterDicts(
                keyFeld='person_id',
                Sort='gruppe_kurz_bez'))
            FL.setHauptformular(form)
            navi.formListen['gruppen'] = FL
            # ... für Versandarten
            def FactoryFormPersonEinzelheitenVersandart():
                uform = Form()
                #
                # Navi herstellen und einsetzen
                unavi = NaviForm(self.frmPersEinzelVersand, elemente=('save', 'delete'))
                uform.setNavi(unavi)
                #
                # Navi konfigurieren
                PG = PersonVersandartSchlank()
                unavi.setGetterValues(PG.FactoryGetterValues())
                unavi.setSaverValues(PG.FactorySaverValues())
                unavi.setDeleterValues(PG.FactorySaverValues())
                unavi.setGetterSelect('versandart', PG.FactoryGetterChoices('versandart'))
                #
                # Widgets
                uform.addWidget(
                    'id',
                    ttk.Entry(self.frmPersEinzelVersand, state=tk.DISABLED, width=6),
                    'int',
                    label='ID')
                uform.addWidget(
                    'person_id',
                    ttk.Entry(self.frmPersEinzelVersand, state=tk.DISABLED, width=6),
                    'int',
                    label='P-ID')
                uform.addWidget(
                    'versandart',
                    ttk.Combobox(self.frmPersEinzelVersand, width=13),
                    'text',
                    label='Versandart'
                    )
                #
                # Formular zurückgeben
                return uform
            FL = FormListeUnterformular(
                self.frmPersEinzelVersand,
                FactoryFormPersonEinzelheitenVersandart,
                linkFeld='person_id',
                linkFeldHauptformular='id'
                )
            FL.setGetterDicts(PersonVersandartSchlank().FactoryGetterDicts(
                keyFeld='person_id',
                Sort='versandart'))
            FL.setHauptformular(form)
            navi.formListen['versandart'] = FL
            #
            # Widgets herstellen, zeigen und in Formular aufnehmen
            form.addWidget(
                'id',
                ttk.Entry(self.frmPersEinzelDaten, state=tk.DISABLED, width=6),
                'int',
                label='ID')
            form.lbl_id.grid(column=0, row=0, sticky=tk.W)
            form.id.grid(column=0, row=1, sticky=tk.W)
            
            form.addWidget(
                'name',
                ttk.Entry(self.frmPersEinzelDaten),
                'text',
                label='Name'
                )
            form.lbl_name.grid(column=0, row=2, sticky=tk.W)
            form.name.grid(column=0, row=3, sticky=tk.W)
            
            form.addWidget(
                'vorname',
                ttk.Entry(self.frmPersEinzelDaten),
                'text',
                label='Vorname'
                )
            form.lbl_vorname.grid(column=1, row=2, columnspan=2, sticky=tk.W)
            form.vorname.grid(column=1, row=3, columnspan=2, sticky=tk.W)
            
            form.addWidget(
                'anrede',
                ttk.Combobox(self.frmPersEinzelDaten, width=10),
                'text',
                label='Anrede'
                )
            form.lbl_anrede.grid(column=3, row=2, sticky=tk.W)
            form.anrede.grid(column=3, row=3, sticky=tk.W)
            
            form.addWidget(
                'von_und_zu',
                ttk.Entry(self.frmPersEinzelDaten, width=10),
                'text',
                label='von, zu...'
                )
            form.lbl_von_und_zu.grid(column=0, row=4, sticky=tk.W)
            form.von_und_zu.grid(column=0, row=5, sticky=tk.W)
            
            form.addWidget(
                'titel',
                ttk.Entry(self.frmPersEinzelDaten, width=10),
                'text',
                label='Dr., Prof.'
                )
            form.lbl_titel.grid(column=1, row=4, sticky=tk.W)
            form.titel.grid(column=1, row=5, sticky=tk.W)
            
            form.addWidget(
                'gebdat',
                ttk.Entry(self.frmPersEinzelDaten,
                      width=15,
                      validate='focusout',
                      validatecommand=(self.valDate, '%P'),
                      invalidcommand=(self.invalidHoldFocus, '%W')
                      ),
                'date',
                label='Geb.-Dat.'
                )
            form.lbl_gebdat.grid(column=2, row=4, sticky=tk.W)
            form.gebdat.grid(column=2, row=5, sticky=tk.W)
            
            form.addWidget(
                'zusatz',
                ttk.Entry(self.frmPersEinzelDaten, width=40),
                'text',
                label='Adresszusatz'
                )
            form.lbl_zusatz.grid(column=0, row=6, columnspan=3, sticky=tk.W)
            form.zusatz.grid(column=0, row=7, columnspan=3, sticky=tk.W)
            
            form.addWidget(
                'strasse',
                ttk.Entry(self.frmPersEinzelDaten),
                'text',
                label='Straße'
                )
            form.lbl_strasse.grid(column=0, row=8, sticky=tk.W)
            form.strasse.grid(column=0, row=9, sticky=tk.W)
            
            form.addWidget(
                'plz',
                ttk.Entry(self.frmPersEinzelDaten, width=6),
                'text',
                label='PLZ'
                )
            form.lbl_plz.grid(column=1, row=8, sticky=tk.W)
            form.plz.grid(column=1, row=9, sticky=tk.W)
            
            form.addWidget(
                'ort',
                ttk.Entry(self.frmPersEinzelDaten),
                'text',
                label='Ort'
                )
            form.lbl_ort.grid(column=2, row=8, sticky=tk.W)
            form.ort.grid(column=2, row=9, sticky=tk.W)
            
            form.addWidget(
                'land',
                ttk.Entry(self.frmPersEinzelDaten),
                'text',
                label='Land'
                )
            form.lbl_land.grid(column=3, row=8, sticky=tk.W)
            form.land.grid(column=3, row=9, sticky=tk.W)
            
            form.addWidget(
                'land_kurz',
                ttk.Entry(self.frmPersEinzelDaten, state=tk.DISABLED, width=4),
                'text',
                label='kurz'
                )
            form.lbl_land_kurz.grid(column=4, row=8, sticky=tk.W)
            form.land_kurz.grid(column=4, row=9, sticky=tk.W)
            
            form.addWidget(
                'email',
                ttk.Entry(self.frmPersEinzelDaten, width=40),
                'text',
                label='eMail'
                )
            form.lbl_email.grid(column=0, row=10, columnspan=3, sticky=tk.W+tk.N)
            form.email.grid(column=0, row=11, columnspan=3, sticky=tk.W+tk.N)
            
            form.addWidget(
                'kontaktdaten',
                scrolledtext.ScrolledText(self.frmPersEinzelDaten, width=50, height=3),
                'text',
                label=ttk.Label(self.frmPersEinzelDaten, text='Kontaktdaten')
                )
            form.lbl_kontaktdaten.grid(column=0, row=12, columnspan=6, sticky=tk.W)
            form.kontaktdaten.grid(column=0, row=13, columnspan=6, sticky=tk.W)
            
            form.addWidget(
                'bemerkung',
                scrolledtext.ScrolledText(self.frmPersEinzelDaten, width=50, height=3),
                'text',
                label=ttk.Label(self.frmPersEinzelDaten, text='Bemerkung')
                )
            form.lbl_bemerkung.grid(column=0, row=14, columnspan=6, sticky=tk.W)
            form.bemerkung.grid(column=0, row=15, columnspan=6, sticky=tk.W)
            
            bearbVonAm = BearbVonAm(self.frmPersEinzelDaten)
            bearbVonAm.grid(column=0, row=16, columnspan=6, sticky=tk.W)
            bearbVonAm.connectToForm(form)
        #
        # Familien Einzelheiten
        with Form() as form:
            glb.formFamilienEinzelheiten = form
            #
            # Frames für Navi, Formular und Unterformulare
            self.frmFamEinzelNavi = ttk.Frame(self.frmFamilienEinzelheiten)
            self.frmFamEinzelDaten = ttk.Frame(self.frmFamilienEinzelheiten)
            self.frmFamEinzelUnterformulare = ttk.Frame(self.frmFamilienEinzelheiten)
            
            self.frmFamEinzelNavi.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            ttk.Separator(self.frmFamilienEinzelheiten, orient=tk.VERTICAL).pack(
                side=tk.LEFT,
                fill=tk.BOTH,
                expand=True)
            self.frmFamEinzelDaten.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            ttk.Separator(self.frmFamilienEinzelheiten, orient=tk.VERTICAL).pack(
                side=tk.LEFT,
                fill=tk.BOTH,
                expand=True)
            self.frmFamEinzelUnterformulare.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            self.sfrFamEinzelGruppen = yScrolledFrame(self.frmFamEinzelUnterformulare)
            self.sfrFamEinzelVersand = yScrolledFrame(self.frmFamEinzelUnterformulare)
            self.frmFamEinzelGruppen = self.sfrFamEinzelGruppen.innerFrame
            self.frmFamEinzelVersand = self.sfrFamEinzelVersand.innerFrame
            ttk.Label(self.frmFamEinzelUnterformulare, text='Gruppen').pack(
                  side=tk.TOP,
                  anchor=tk.W)
            self.sfrFamEinzelGruppen.pack(side=tk.TOP, fill=tk.BOTH)
            ttk.Separator(self.frmFamEinzelUnterformulare, orient=tk.HORIZONTAL).pack(
                side=tk.TOP,
                expand=True,
                fill=tk.BOTH)
            ttk.Label(self.frmFamEinzelUnterformulare, text='Versandarten').pack(
                side=tk.TOP,
                anchor=tk.W)
            self.sfrFamEinzelVersand.pack(side=tk.TOP, fill=tk.BOTH)
            
            self.frmFamEinzelGruppen.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            self.frmFamEinzelVersand.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            #
            # Navi herstellen und einsetzen
            navi = NaviForm(self.frmFamEinzelNavi)
            form.setNavi(navi)
            navi.pack(fill=tk.BOTH, expand=True)
            #
            # Navi konfigurieren
            F = Familie()
            navi.setGetterAuswahl(F.FactoryGetterAuswahl(
                'id',
                ('name', 'id',),
                ('name', 'strasse', 'ort',),
                'name'
                ))
            navi.setGetterValues(F.FactoryGetterValues())
            navi.setSaverValues(F.FactorySaverValues())
            navi.setDeleterValues(F.FactoryDeleterValues())
            navi.setGetterSelect('anrede', F.FactoryGetterChoices('anrede'))
            #
            # Unterformulare herstellen und an Navi hängen
            #
            # ... für Gruppen
            def FactoryFormFamilieEinzelheitenGruppe():
                uform = Form()
                #
                # Navi herstellen und einsetzen
                unavi = NaviForm(self.frmFamEinzelGruppen, elemente=('save', 'delete'))
                uform.setNavi(unavi)
                #
                # Navi konfigurieren
                FG = FamilieGruppeSchlank()
                unavi.setGetterValues(FG.FactoryGetterValues())
                unavi.setSaverValues(FG.FactorySaverValues())
                unavi.setDeleterValues(FG.FactoryDeleterValues())
                unavi.setGetterSelect('gruppe_kurz_bez', FG.FactoryGetterChoices('gruppe_kurz_bez'))
                #
                # Widgets
                uform.addWidget(
                    'id',
                    ttk.Entry(self.frmFamEinzelGruppen, state=tk.DISABLED, width=6),
                    'int',
                    label='ID')
                uform.addWidget(
                    'familie_id',
                    ttk.Entry(self.frmFamEinzelGruppen, state=tk.DISABLED, width=6),
                    'int',
                    label='F-ID')
                uform.addWidget(
                    'gruppe_kurz_bez',
                    ttk.Combobox(self.frmFamEinzelGruppen, width=10),
                    'text',
                    label='Gruppe'
                    )
                #
                # Formular zurückgeben
                return uform
            FL = FormListeUnterformular(
                self.frmFamEinzelGruppen,
                FactoryFormFamilieEinzelheitenGruppe,
                linkFeld='familie_id',
                linkFeldHauptformular='id'
                )
            FL.setGetterDicts(FamilieGruppeSchlank().FactoryGetterDicts(
                keyFeld='familie_id',
                Sort='gruppe_kurz_bez'))
            FL.setHauptformular(form)
            navi.formListen['gruppen'] = FL
            # ... für Versandarten
            def FactoryFormFamilieEinzelheitenVersandart():
                uform = Form()
                #
                # Navi herstellen und einsetzen
                unavi = NaviForm(self.frmFamEinzelVersand, elemente=('save', 'delete'))
                uform.setNavi(unavi)
                #
                # Navi konfigurieren
                FV = FamilieVersandartSchlank()
                unavi.setGetterValues(FV.FactoryGetterValues())
                unavi.setSaverValues(FV.FactorySaverValues())
                unavi.setDeleterValues(FV.FactorySaverValues())
                unavi.setGetterSelect('versandart', FV.FactoryGetterChoices('versandart'))
                #
                # Widgets
                uform.addWidget(
                    'id',
                    ttk.Entry(self.frmFamEinzelVersand, state=tk.DISABLED, width=6),
                    'int',
                    label='ID')
                uform.addWidget(
                    'familie_id',
                    ttk.Entry(self.frmFamEinzelVersand, state=tk.DISABLED, width=6),
                    'int',
                    label='P-ID')
                uform.addWidget(
                    'versandart',
                    ttk.Combobox(self.frmFamEinzelVersand, width=13),
                    'text',
                    label='Versandart'
                    )
                #
                # Formular zurückgeben
                return uform
            FL = FormListeUnterformular(
                self.frmFamEinzelVersand,
                FactoryFormFamilieEinzelheitenVersandart,
                linkFeld='familie_id',
                linkFeldHauptformular='id'
                )
            FL.setGetterDicts(FamilieVersandartSchlank().FactoryGetterDicts(
                keyFeld='familie_id',
                Sort='versandart'))
            FL.setHauptformular(form)
            navi.formListen['versandart'] = FL
            #
            # Widgets herstellen, zeigen und in Formular aufnehmen
            form.addWidget(
                'id',
                ttk.Entry(self.frmFamEinzelDaten, state=tk.DISABLED, width=6),
                'int',
                label='ID')
            form.lbl_id.grid(column=0, row=0, sticky=tk.W)
            form.id.grid(column=0, row=1, sticky=tk.W)
            
            form.addWidget(
                'name',
                ttk.Entry(self.frmFamEinzelDaten),
                'text',
                label='Name (nur Sortierung)'
                )
            form.lbl_name.grid(column=0, row=2, sticky=tk.W)
            form.name.grid(column=0, row=3, sticky=tk.W)
            
            form.addWidget(
                'anschrift',
                ttk.Entry(self.frmFamEinzelDaten),
                'text',
                label='Name Etikett'
                )
            form.lbl_anschrift.grid(column=1, row=2, columnspan=2, sticky=tk.W)
            form.anschrift.grid(column=1, row=3, columnspan=2, sticky=tk.W)
            
            form.addWidget(
                'anrede',
                ttk.Combobox(self.frmFamEinzelDaten, width=10),
                'text',
                label='Anrede'
                )
            form.lbl_anrede.grid(column=3, row=2, sticky=tk.W)
            form.anrede.grid(column=3, row=3, sticky=tk.W)
            
            form.addWidget(
                'zusatz',
                ttk.Entry(self.frmFamEinzelDaten, width=40),
                'text',
                label='Adresszusatz'
                )
            form.lbl_zusatz.grid(column=0, row=4, columnspan=3, sticky=tk.W)
            form.zusatz.grid(column=0, row=5, columnspan=3, sticky=tk.W)
            
            form.addWidget(
                'strasse',
                ttk.Entry(self.frmFamEinzelDaten),
                'text',
                label='Straße'
                )
            form.lbl_strasse.grid(column=0, row=6, sticky=tk.W)
            form.strasse.grid(column=0, row=7, sticky=tk.W)
            
            form.addWidget(
                'plz',
                ttk.Entry(self.frmFamEinzelDaten, width=6),
                'text',
                label='PLZ'
                )
            form.lbl_plz.grid(column=1, row=6, sticky=tk.W)
            form.plz.grid(column=1, row=7, sticky=tk.W)
            
            form.addWidget(
                'ort',
                ttk.Entry(self.frmFamEinzelDaten),
                'text',
                label='Ort'
                )
            form.lbl_ort.grid(column=2, row=6, sticky=tk.W)
            form.ort.grid(column=2, row=7, sticky=tk.W)
            
            form.addWidget(
                'land',
                ttk.Entry(self.frmFamEinzelDaten),
                'text',
                label='Land'
                )
            form.lbl_land.grid(column=3, row=6, sticky=tk.W)
            form.land.grid(column=3, row=7, sticky=tk.W)
            
            form.addWidget(
                'land_kurz',
                ttk.Entry(self.frmFamEinzelDaten, state=tk.DISABLED, width=4),
                'text',
                label='kurz'
                )
            form.lbl_land_kurz.grid(column=4, row=6, sticky=tk.W)
            form.land_kurz.grid(column=4, row=7, sticky=tk.W)
            
            form.addWidget(
                'email',
                ttk.Entry(self.frmFamEinzelDaten, width=40),
                'text',
                label='eMail'
                )
            form.lbl_email.grid(column=0, row=8, columnspan=3, sticky=tk.W+tk.N)
            form.email.grid(column=0, row=9, columnspan=3, sticky=tk.W+tk.N)
            
            form.addWidget(
                'kontaktdaten',
                scrolledtext.ScrolledText(self.frmFamEinzelDaten, width=50, height=3),
                'text',
                label=ttk.Label(self.frmFamEinzelDaten, text='Kontaktdaten')
                )
            form.lbl_kontaktdaten.grid(column=0, row=10, columnspan=6, sticky=tk.W)
            form.kontaktdaten.grid(column=0, row=11, columnspan=6, sticky=tk.W)
            
            form.addWidget(
                'bemerkung',
                scrolledtext.ScrolledText(self.frmFamEinzelDaten, width=50, height=3),
                'text',
                label=ttk.Label(self.frmFamEinzelDaten, text='Bemerkung')
                )
            form.lbl_bemerkung.grid(column=0, row=12, columnspan=6, sticky=tk.W)
            form.bemerkung.grid(column=0, row=13, columnspan=6, sticky=tk.W)
            
            bearbVonAm = BearbVonAm(self.frmFamEinzelDaten)
            bearbVonAm.grid(column=0, row=14, columnspan=6, sticky=tk.W)
            bearbVonAm.connectToForm(form)
        #
        # Gruppen
        with Form() as form:
            glb.formGruppen = form
            #
            # Frames für Navi und Formular bauen und in PanedWindow einsetzen
            self.frmGruppenNavi = ttk.Frame(self.frmGruppenEinzelheiten)
            self.frmGruppenDaten = ttk.Frame(self.frmGruppenEinzelheiten)
            self.frmGruppenEinzelheiten.add(self.frmGruppenNavi)
            self.frmGruppenEinzelheiten.add(self.frmGruppenDaten)
            #
            # Navi herstellen und einsetzen
            navi = NaviForm(self.frmGruppenNavi)
            form.setNavi(navi)
            navi.pack(fill=tk.BOTH, expand=True)
            #
            # Navi konfigurieren
            G = Gruppe()
            navi.setGetterAuswahl(G.FactoryGetterAuswahl(
                'id',
                ('kurz_bez', 'bez'),
                ('kurz_bez', 'bez'),
                'kurz_bez'
                ))
            navi.setGetterValues(G.FactoryGetterValues())
            navi.setSaverValues(G.FactorySaverValues())
            navi.setDeleterValues(G.FactoryDeleterValues())
            navi.setGetterSelect('farbe', G.FactoryGetterChoices('farbe'))
            #
            # Widgets herstellen, zeigen und in Formular aufnehmen
            form.addWidget(
                'id',
                ttk.Entry(self.frmGruppenDaten, state=tk.DISABLED),
                'int',
                label='ID')
            form.lbl_id.grid(column=0, row=0, sticky=tk.E)
            form.id.grid(column=1, row=0, sticky=tk.W)
            
            form.addWidget(
                'kurz_bez',
                ttk.Entry(self.frmGruppenDaten),
                'text',
                label='Kurz.-Bez.')
            form.lbl_kurz_bez.grid(column=0, row=1, sticky=tk.E)
            form.kurz_bez.grid(column=1, row=1, sticky=tk.W)
            
            form.addWidget(
                'bez',
                ttk.Entry(self.frmGruppenDaten),
                'text',
                label='Bezeichnung')
            form.lbl_bez.grid(column=0, row=2, sticky=tk.E)
            form.bez.grid(column=1, row=2, sticky=tk.W)
            
            form.addWidget(
                'farbe',
                ttk.Combobox(self.frmGruppenDaten),
                'text',
                label='Farbe')
            form.lbl_farbe.grid(column=0, row=3, sticky=tk.E)
            form.farbe.grid(column=1, row=3, sticky=tk.W)
            
            form.addWidget(
                'bemerkung',
                scrolledtext.ScrolledText(self.frmGruppenDaten, width=25, height=5),
                'text',
                label=ttk.Label(self.frmGruppenDaten, text='Bemerkung'))
            form.lbl_bemerkung.grid(column=0, row=4, sticky=tk.E+tk.N)
            form.bemerkung.grid(column=1, row=4, sticky=tk.W)
            
            bearbVonAm = BearbVonAm(self.frmGruppenDaten)
            bearbVonAm.grid(column=0, row=5, columnspan=2, sticky=tk.W)
            bearbVonAm.connectToForm(form)
        #
        # Gruppen als Liste
        def FactoryGruppeListe():
            form = Form()
            #
            # Navi herstellen und einsetzen
            navi = NaviForm(self.frmGruppenListeInhalt.innerFrame, elemente=('save', 'delete'))
            form.setNavi(navi)
            #
            # Navi konfigurieren
            G = GruppeSchlank()
            navi.setGetterValues(G.FactoryGetterValues())
            navi.setSaverValues(G.FactorySaverValues())
            navi.setDeleterValues(G.FactoryDeleterValues())
            navi.setGetterSelect(
                'farbe',
                G.FactoryGetterChoices('farbe')
                )
            #
            # Widgets
            form.addWidget(
                'id',
                ttk.Entry(self.frmGruppenListeInhalt.innerFrame, state=tk.DISABLED, width=6),
                'int',
                label='ID')
            form.addWidget(
                'kurz_bez',
                ttk.Entry(self.frmGruppenListeInhalt.innerFrame, width=10),
                'text',
                label='Kurz.-Bez.')
            form.addWidget(
                'bez',
                ttk.Entry(self.frmGruppenListeInhalt.innerFrame, width=20),
                'text',
                label='Bezeichnung')
            form.addWidget(
                'farbe',
                ttk.Combobox(self.frmGruppenListeInhalt.innerFrame, width=10),
                'text',
                label='Farbe')
            #
            # Formular zurückgeben
            return form
                
        with FormListe(self.frmGruppenListeInhalt.innerFrame, FactoryGruppeListe) as form:
            glb.formGruppenListe = form
            #
            # Navi herstellen und einsetzen
            navi = NaviListe(self.frmGruppenListeNavi)
            form.setNavi(navi)
            #
            # Navi konfigurieren
            G = GruppeSchlank()
            navi.setGetterDicts(G.FactoryGetterDicts(FilterFelder=('kurz_bez', 'bez'), Sort='kurz_bez'))
            #
            # Form Navi packen
            form.getNavi().pack(anchor=tk.W)
        #
        # Versandarten
        with Form() as form:
            glb.formVersandarten = form
            #
            # Frames für Navi und Formular bauen und in PanedWindow einsetzen
            self.frmVersandartenNavi = ttk.Frame(self.frmVersandartenEinzelheiten)
            self.frmVersandartenDaten = ttk.Frame(self.frmVersandartenEinzelheiten)
            self.frmVersandartenEinzelheiten.add(self.frmVersandartenNavi)
            self.frmVersandartenEinzelheiten.add(self.frmVersandartenDaten)
            #
            # Navi herstellen und einsetzen
            navi = NaviForm(self.frmVersandartenNavi)
            form.setNavi(navi)
            navi.pack(fill=tk.BOTH, expand=True)
            #
            # Navi konfigurieren
            V = Versandart()
            navi.setGetterAuswahl(V.FactoryGetterAuswahl(
                'id',
                ('kurz_bez', 'bez'),
                ('kurz_bez', 'bez'),
                'kurz_bez'
                ))
            navi.setGetterValues(V.FactoryGetterValues())
            navi.setSaverValues(V.FactorySaverValues())
            navi.setDeleterValues(V.FactoryDeleterValues())
            #
            # Widgets herstellen, zeigen und in Formular aufnehmen
            form.addWidget(
                'id',
                ttk.Entry(self.frmVersandartenDaten, state=tk.DISABLED),
                'int',
                label='ID')
            form.lbl_id.grid(column=0, row=0, sticky=tk.E)
            form.id.grid(column=1, row=0, sticky=tk.W)
            
            form.addWidget(
                'kurz_bez',
                ttk.Entry(self.frmVersandartenDaten),
                'text',
                label='Kurz.-Bez.')
            form.lbl_kurz_bez.grid(column=0, row=1, sticky=tk.E)
            form.kurz_bez.grid(column=1, row=1, sticky=tk.W)
            
            form.addWidget(
                'bez',
                ttk.Entry(self.frmVersandartenDaten),
                'text',
                label='Bezeichnung')
            form.lbl_bez.grid(column=0, row=2, sticky=tk.E)
            form.bez.grid(column=1, row=2, sticky=tk.W)
            
            form.addWidget(
                'bemerkung',
                scrolledtext.ScrolledText(self.frmVersandartenDaten, width=25, height=5),
                'text',
                label=ttk.Label(self.frmVersandartenDaten, text='Bemerkung'))
            form.lbl_bemerkung.grid(column=0, row=4, sticky=tk.E+tk.N)
            form.bemerkung.grid(column=1, row=4, sticky=tk.W)
            
            bearbVonAm = BearbVonAm(self.frmVersandartenDaten)
            bearbVonAm.grid(column=0, row=5, columnspan=2, sticky=tk.W)
            bearbVonAm.connectToForm(form)
            
        #
        # Anreden
        with Form() as form:
            glb.formAnreden = form
            #
            # Frames für Navi und Formular bauen und in PanedWindow einsetzen
            self.frmAnredenNavi = ttk.Frame(self.frmAnredenEinzelheiten)
            self.frmAnredenDaten = ttk.Frame(self.frmAnredenEinzelheiten)
            self.frmAnredenEinzelheiten.add(self.frmAnredenNavi)
            self.frmAnredenEinzelheiten.add(self.frmAnredenDaten)
            #
            # Navi herstellen und einsetzen
            navi = NaviForm(self.frmAnredenNavi)
            form.setNavi(navi)
            navi.pack(fill=tk.BOTH, expand=True)
            #
            # Navi konfigurieren
            A = Anrede()
            navi.setGetterAuswahl(A.FactoryGetterAuswahl(
                'id',
                ('anrede',),
                ('anrede',),
                'anrede'
                ))
            navi.setGetterValues(A.FactoryGetterValues())
            navi.setSaverValues(A.FactorySaverValues())
            navi.setDeleterValues(A.FactoryDeleterValues())
            #
            # Widgets herstellen, zeigen und in Formular aufnehmen
            form.addWidget(
                'id',
                ttk.Entry(self.frmAnredenDaten, state=tk.DISABLED),
                'int',
                label='ID')
            form.lbl_id.grid(column=0, row=0, sticky=tk.E)
            form.id.grid(column=1, row=0, sticky=tk.W)
            
            form.addWidget(
                'anrede',
                ttk.Entry(self.frmAnredenDaten),
                'text',
                label='Anrede')
            form.lbl_anrede.grid(column=0, row=1, sticky=tk.E)
            form.anrede.grid(column=1, row=1, sticky=tk.W)
            
            bearbVonAm = BearbVonAm(self.frmAnredenDaten)
            bearbVonAm.grid(column=0, row=5, columnspan=2, sticky=tk.W)
            bearbVonAm.connectToForm(form)
            
        #
        # Farben
        with Form() as form:
            glb.formFarben = form
            #
            # Frames für Navi und Formular bauen und in PanedWindow einsetzen
            self.frmFarbenNavi = ttk.Frame(self.frmFarbenEinzelheiten)
            self.frmFarbenDaten = ttk.Frame(self.frmFarbenEinzelheiten)
            self.frmFarbenEinzelheiten.add(self.frmFarbenNavi)
            self.frmFarbenEinzelheiten.add(self.frmFarbenDaten)
            #
            # Navi herstellen und einsetzen
            navi = NaviForm(self.frmFarbenNavi)
            form.setNavi(navi)
            navi.pack(fill=tk.BOTH, expand=True)
            #
            # Navi konfigurieren
            F = Farbe()
            navi.setGetterAuswahl(F.FactoryGetterAuswahl(
                'id',
                ('farbe',),
                ('farbe',),
                'farbe'
                ))
            navi.setGetterValues(F.FactoryGetterValues())
            navi.setSaverValues(F.FactorySaverValues())
            navi.setDeleterValues(F.FactoryDeleterValues())
            #
            # Widgets herstellen, zeigen und in Formular aufnehmen
            form.addWidget(
                'id',
                ttk.Entry(self.frmFarbenDaten, state=tk.DISABLED),
                'int',
                label='ID')
            form.lbl_id.grid(column=0, row=0, sticky=tk.E)
            form.id.grid(column=1, row=0, sticky=tk.W)
            
            form.addWidget(
                'farbe',
                ttk.Entry(self.frmFarbenDaten),
                'text',
                label='Farbe')
            form.lbl_farbe.grid(column=0, row=1, sticky=tk.E)
            form.farbe.grid(column=1, row=1, sticky=tk.W)
            
            bearbVonAm = BearbVonAm(self.frmFarbenDaten)
            bearbVonAm.grid(column=0, row=2, columnspan=2, sticky=tk.W)
            bearbVonAm.connectToForm(form)
            #
            # Info-Widget zu Farben herstellen und zeigen
            infoText = 'Nur Farben aus dem x11names Bereich, s. z.B.\n'
            urlText = 'https://ctan.math.washington.edu/tex-archive/macros/latex/contrib/xcolor/xcolor.pdf'
            wdg = scrolledtext.ScrolledText(
                self.frmFarbenDaten,
                width=70,
                height=4)
            wdg.insert('0.0', urlText)
            wdg.insert('0.0', infoText)
            ttk.Label(self.frmFarbenDaten, text='Info').grid(column=3, row=0, sticky=tk.W)
            wdg.grid(column=3, row=1, rowspan=2, sticky=tk.W)
            wdg.config(state=tk.DISABLED)
            
        #
        # Gemeinden
        with Form() as form:
            glb.formGemeinden = form
            #
            # Frames für Navi und Formular bauen und in PanedWindow einsetzen
            self.frmGemeindenNavi = ttk.Frame(self.frmGemeindenEinzelheiten)
            self.frmGemeindenDaten = ttk.Frame(self.frmGemeindenEinzelheiten)
            self.frmGemeindenEinzelheiten.add(self.frmGemeindenNavi)
            self.frmGemeindenEinzelheiten.add(self.frmGemeindenDaten)
            #
            # Navi herstellen und einsetzen
            navi = NaviForm(self.frmGemeindenNavi)
            form.setNavi(navi)
            navi.pack(fill=tk.BOTH, expand=True)
            #
            # Navi konfigurieren
            G = Gemeinde()
            navi.setGetterAuswahl(G.FactoryGetterAuswahl(
                'id',
                ('kurz_bez',),
                ('kurz_bez',),
                'kurz_bez'
                ))
            navi.setGetterValues(G.FactoryGetterValues())
            navi.setSaverValues(G.FactorySaverValues())
            navi.setDeleterValues(G.FactoryDeleterValues())
            #
            # Widgets herstellen, zeigen und in Formular aufnehmen
            form.addWidget(
                'id',
                ttk.Entry(self.frmGemeindenDaten, state=tk.DISABLED, width=6),
                'int',
                label='ID')
            form.lbl_id.grid(column=0, row=0, sticky=tk.W)
            form.id.grid(column=0, row=1, sticky=tk.W)
            
            form.addWidget(
                'kurz_bez',
                ttk.Entry(self.frmGemeindenDaten, width=40),
                'text',
                label='Bezeichnung')
            form.lbl_kurz_bez.grid(column=0, row=2, columnspan=2, sticky=tk.W)
            form.kurz_bez.grid(column=0, row=3, columnspan=2, sticky=tk.W)
            
            form.addWidget(
                'aktiv',
                ttk.Checkbutton(self.frmGemeindenDaten),
                'bool',
                label='aktiv')
            form.lbl_aktiv.grid(column=3, row=2, sticky=tk.W)
            form.aktiv.grid(column=3, row=3, sticky=tk.W)
            
            form.addWidget(
                'strasse',
                ttk.Entry(self.frmGemeindenDaten),
                'text',
                label='Straße'
                )
            form.lbl_strasse.grid(column=0, row=4, sticky=tk.W)
            form.strasse.grid(column=0, row=5, sticky=tk.W)
            
            form.addWidget(
                'plz',
                ttk.Entry(self.frmGemeindenDaten, width=6),
                'text',
                label='PLZ'
                )
            form.lbl_plz.grid(column=1, row=4, sticky=tk.W)
            form.plz.grid(column=1, row=5, sticky=tk.W)
            
            form.addWidget(
                'ort',
                ttk.Entry(self.frmGemeindenDaten),
                'text',
                label='Ort'
                )
            form.lbl_ort.grid(column=2, row=4, sticky=tk.W)
            form.ort.grid(column=2, row=5, sticky=tk.W)
            
            form.addWidget(
                'land',
                ttk.Entry(self.frmGemeindenDaten),
                'text',
                label='Land'
                )
            form.lbl_land.grid(column=3, row=4, sticky=tk.W)
            form.land.grid(column=3, row=5, sticky=tk.W)
            
            form.addWidget(
                'land_kurz',
                ttk.Entry(self.frmGemeindenDaten, state=tk.DISABLED, width=4),
                'text',
                label='kurz'
                )
            form.lbl_land_kurz.grid(column=4, row=4, sticky=tk.W)
            form.land_kurz.grid(column=4, row=5, sticky=tk.W)
            
            form.addWidget(
                'email',
                ttk.Entry(self.frmGemeindenDaten, width=40),
                'text',
                label='eMail'
                )
            form.lbl_email.grid(column=0, row=6, columnspan=2, sticky=tk.W)
            form.email.grid(column=0, row=7, columnspan=2, sticky=tk.W)
            
            form.addWidget(
                'rel_verz',
                ttk.Entry(self.frmGemeindenDaten),
                'text',
                label='Rel. Verz.')
            form.lbl_rel_verz.grid(column=2, row=6, sticky=tk.W)
            form.rel_verz.grid(column=2, row=7, sticky=tk.W)
            
            form.addWidget(
                'mail_from',
                ttk.Entry(self.frmGemeindenDaten),
                'text',
                label='Mail From')
            form.lbl_mail_from.grid(column=0, row=8, sticky=tk.W)
            form.mail_from.grid(column=0, row=9, sticky=tk.W)
            
            form.addWidget(
                'mail_reply',
                ttk.Entry(self.frmGemeindenDaten),
                'text',
                label='Mail Reply')
            form.lbl_mail_reply.grid(column=1, row=8, sticky=tk.W)
            form.mail_reply.grid(column=1, row=9, sticky=tk.W)
            
            form.addWidget(
                'mail_signatur',
                scrolledtext.ScrolledText(self.frmGemeindenDaten, width=40, height=7),
                'text',
                label=ttk.Label(self.frmGemeindenDaten, text='Mail Signatur'))
            form.lbl_mail_signatur.grid(column=4, row=8, sticky=tk.W)
            form.mail_signatur.grid(column=4, row=9, rowspan=7, sticky=tk.W+tk.N)
            
            form.addWidget(
                'smtp_server',
                ttk.Entry(self.frmGemeindenDaten),
                'text',
                label='SMTP Server')
            form.lbl_smtp_server.grid(column=0, row=10, sticky=tk.W)
            form.smtp_server.grid(column=0, row=11, sticky=tk.W)
            
            form.addWidget(
                'smtp_port',
                ttk.Entry(self.frmGemeindenDaten),
                'text',
                label='SMTP Port')
            form.lbl_smtp_port.grid(column=1, row=10, sticky=tk.W)
            form.smtp_port.grid(column=1, row=11, sticky=tk.W)
            
            form.addWidget(
                'smtp_user',
                ttk.Entry(self.frmGemeindenDaten),
                'text',
                label='SMTP User')
            form.lbl_smtp_user.grid(column=2, row=10, sticky=tk.W)
            form.smtp_user.grid(column=2, row=11, sticky=tk.W)
            
            form.addWidget(
                'smtp_password',
                ttk.Entry(self.frmGemeindenDaten, show='*'),
                'text',
                label='SMTP Password')
            form.lbl_smtp_password.grid(column=3, row=10, sticky=tk.W)
            form.smtp_password.grid(column=3, row=11, sticky=tk.W)
            
            form.addWidget(
                'schema',
                ttk.Entry(self.frmGemeindenDaten),
                'text',
                label='DB Schema')
            form.lbl_schema.grid(column=0, row=12, sticky=tk.W)
            form.schema.grid(column=0, row=13, sticky=tk.W)
            
            bearbVonAm = BearbVonAm(self.frmGemeindenDaten)
            bearbVonAm.grid(column=0, row=14, columnspan=2, sticky=tk.W)
            bearbVonAm.connectToForm(form)
        #
        # Jobs Einzelheiten
        with Form() as form:
            glb.formJobsEinzelheiten = form
            #
            # Frames für Navi und Formular bauen und in PanedWindow einsetzen
            self.frmJobsEinzelheitenNavi = ttk.Frame(self.frmJobsEinzelheiten)
            self.frmJobsEinzelheitenDaten = ttk.Frame(self.frmJobsEinzelheiten)
            
            self.frmJobsEinzelheiten.add(self.frmJobsEinzelheitenNavi)
            self.frmJobsEinzelheiten.add(self.frmJobsEinzelheitenDaten)
            #
            # Navi herstellen und einsetzen
            navi = NaviForm(self.frmJobsEinzelheitenNavi)
            form.setNavi(navi)
            navi.pack(fill=tk.BOTH, expand=True)
            #
            # Navi konfigurieren
            J = Jobs()
            navi.setGetterAuswahl(J.FactoryGetterAuswahl(
                'id',
                ('titel',),
                ('titel', 'kommando',),
                'kommando'
                ))
            navi.setGetterValues(J.FactoryGetterValues())
            navi.setSaverValues(J.FactorySaverValues())
            navi.setDeleterValues(J.FactoryDeleterValues())
            #
            # Widgets herstellen, zeigen und in Formular aufnehmen
            form.addWidget(
                'id',
                ttk.Entry(self.frmJobsEinzelheitenDaten, state=tk.DISABLED, width=6),
                'int',
                label='ID')
            form.lbl_id.grid(column=0, row=0, sticky=tk.W)
            form.id.grid(column=0, row=1, sticky=tk.W)
            
            form.addWidget(
                'titel',
                ttk.Entry(self.frmJobsEinzelheitenDaten, width=40),
                'text',
                label='Titel')
            form.lbl_titel.grid(column=0, row=2, columnspan=2, sticky=tk.W)
            form.titel.grid(column=0, row=3, columnspan=2, sticky=tk.W)
            
            form.addWidget(
                'kommando',
                ttk.Entry(self.frmJobsEinzelheitenDaten, width=40),
                'text',
                label='Kommando')
            form.lbl_kommando.grid(column=0, row=4, sticky=tk.W)
            form.kommando.grid(column=0, row=5, sticky=tk.W)
            
            form.addWidget(
                'verzeichnis',
                ttk.Entry(self.frmJobsEinzelheitenDaten, width=40),
                'text',
                label='Verzeichnis')
            form.lbl_verzeichnis.grid(column=2, row=4, sticky=tk.W)
            form.verzeichnis.grid(column=2, row=5, sticky=tk.W)
            
            form.addWidget(
                'beschreibung',
                ttk.Entry(self.frmJobsEinzelheitenDaten, width=80),
                'text',
                label='Beschreibung')
            form.lbl_beschreibung.grid(column=0, row=6, columnspan=3, sticky=tk.W)
            form.beschreibung.grid(column=0, row=7, columnspan=3, sticky=tk.W)
            
            form.addWidget(
                'intervall',
                ttk.Entry(
                      self.frmJobsEinzelheitenDaten,
                      width=4,
                      validate='key',
                      validatecommand=(self.valInt, '%P')
                      ),
                'int',
                label='Intervall')
            form.lbl_intervall.grid(column=0, row=8, sticky=tk.E)
            form.intervall.grid(column=0, row=9, sticky=tk.E)
            
            form.addWidget(
                'einheit',
                ComboboxValueLabel(
                      self.frmJobsEinzelheitenDaten,
                      width=12),
                'text',
                label='Einheit')
            form.getWidget('einheit').fill((
                ('mi', 'Minute(n)'),
                ('st', 'Stunde(n)'),
                ('ta', 'Tag(e)'),
                ('mo', 'Monat(e)')
                ))
            form.lbl_einheit.grid(column=1, row=8, sticky=tk.W)
            form.einheit.grid(column=1, row=9, sticky=tk.W)
            
            form.addWidget(
                'aktiv',
                ttk.Checkbutton(self.frmJobsEinzelheitenDaten),
                'bool',
                label='Aktiv')
            form.lbl_aktiv.grid(column=0, row=10, sticky=tk.E)
            form.aktiv.grid(column=1, row=10, sticky=tk.W)
                
            form.addWidget(
                'sofort',
                ttk.Checkbutton(self.frmJobsEinzelheitenDaten),
                'bool',
                label='Sofort')
            form.lbl_sofort.grid(column=0, row=11, sticky=tk.E)
            form.sofort.grid(column=1, row=11, sticky=tk.W)
                
            form.addWidget(
                'gestoppt',
                ttk.Checkbutton(self.frmJobsEinzelheitenDaten),
                'bool',
                label='Gestoppt')
            form.lbl_gestoppt.grid(column=0, row=12, sticky=tk.E)
            form.gestoppt.grid(column=1, row=12, sticky=tk.W)
                
            form.addWidget(
                'selbstzerstoerend',
                ttk.Checkbutton(self.frmJobsEinzelheitenDaten),
                'bool',
                label='Selbstzerstörend')
            form.lbl_selbstzerstoerend.grid(column=0, row=13, sticky=tk.E)
            form.selbstzerstoerend.grid(column=1, row=13, sticky=tk.W)
        #
        # Jobs Liste
        def FactoryJobsListe():
            form = Form()
            #
            # Navi herstellen und einsetzen
            navi = NaviForm(self.frmJobsListeInhalt.innerFrame, elemente=('save', 'delete'))
            form.setNavi(navi)
            #
            # Navi konfigurieren
            J = JobsSchlank()
            navi.setGetterValues(J.FactoryGetterValues())
            navi.setSaverValues(J.FactorySaverValues())
            navi.setDeleterValues(J.FactoryDeleterValues())
            #
            # Widgets
            form.addWidget(
                'id',
                ttk.Entry(self.frmJobsListeInhalt.innerFrame, state=tk.DISABLED, width=6),
                'int',
                label='ID')
            form.addWidget(
                'titel',
                ttk.Entry(self.frmJobsListeInhalt.innerFrame, width=30),
                'text',
                label='Titel')
            form.addWidget(
                'kommando',
                ttk.Entry(self.frmJobsListeInhalt.innerFrame, width=30),
                'text',
                label='Kommando')
            form.addWidget(
                'intervall',
                ttk.Entry(
                      self.frmJobsListeInhalt.innerFrame,
                      width=8,
                      validate='key',
                      validatecommand=(self.valInt, '%P')
                      ),
                'int',
                label='Interv.')
            form.addWidget(
                'einheit',
                ComboboxValueLabel(
                      self.frmJobsListeInhalt.innerFrame,
                      width=12),
                'text',
                label='Einheit')
            form.getWidget('einheit').fill((
                ('mi', 'Minute(n)'),
                ('st', 'Stunde(n)'),
                ('ta', 'Tag(e)'),
                ('mo', 'Monat(e)')
                ))
            form.addWidget(
                'aktiv',
                ttk.Checkbutton(self.frmJobsListeInhalt.innerFrame),
                'bool',
                label='Aktiv')
            form.addWidget(
                'sofort',
                ttk.Checkbutton(self.frmJobsListeInhalt.innerFrame),
                'bool',
                label='Sofort')
            form.addWidget(
                'gestoppt',
                ttk.Checkbutton(self.frmJobsListeInhalt.innerFrame),
                'bool',
                label='Gestoppt')
            #
            # Formular zurückgeben
            return form
        
        with FormListe(self.frmJobsListeInhalt.innerFrame, FactoryJobsListe) as form:
            glb.formGruppenListe = form
            #
            # Navi herstellen und einsetzen
            navi = NaviListe(self.frmJobsListeNavi)
            form.setNavi(navi)
            #
            # Navi konfigurieren
            J = JobsSchlank()
            navi.setGetterDicts(J.FactoryGetterDicts(
                    FilterFelder=('titel', 'kommando'),
                    Sort='kommando'))
            #
            # Form Navi packen
            form.getNavi().pack(anchor=tk.W)
            
        #
        # Mail Versand
        with Form() as form:
            glb.formMailVersand = form
            self.mailAttachments = []
            #
            # Methoden - Button Handler
            def handleMailAnhang():
                """handleMailAnhang - Bringt eine (weitere) Datei in Liste der Anhänge
                
                    Ruft filedialog.askopenfilename auf und ergänzt die Liste der
                    Anhänge um den ausgewählten Dateinamen. Die Liste wird anschließend
                    in der UI angezeigt.
                    
                    Die Liste der Anhänge wird in der Liste (list)
                        self.mailAttachments
                    geführt. Sie sie besteht aus Tupeln der Form
                        (path, basename)
                    mit
                        path      Vollständiger Pfad
                        basename  Dateiname
                """
                filename = filedialog.askopenfilename(
                    title='Datei als Anhang aufwählen',
                    filetypes=[('PNG', '*.png'), ('Python', '*.py'), ('PDF', '*,pdf')]
                    )
                if filename:
                    # nur, wenn auch tatsächlich eine Datei ausgewählt wurde:
                    self.mailAttachments.append((filename, os.path.basename(filename)))
                # Liste zeigen
                liste = ', '.join([name for (value, name) in self.mailAttachments])
                glb.formMailVersand.setValue('anhang', liste)
            
            def handleMailAnhangClear():
                """handleMailAnhangClear - Löscht die Liste der Anhänge
                
                    Löscht die Liste der Anhänge und entsprechend auch deren Anzeige
                    in der UI
                """
                attachments = []
                glb.formMailVersand.clearValue('anhang')
            
            def handleMailCheck():
                """handleMailCheck - Zeigt die Liste der Empfänger zum Überprüfen
                
                    Zeigt die Liste der Empfänger, damit sie (stichprobenhaft)
                    überprüft werden kann. Das ist v.a. bei großen Versänden sinnvoll...
                """
                notify('=======================================')
                notify('Mail Verteiler Checken')
                notify('=======================================')
                self.mailVerteiler = getMailVerteiler()
                emailCounter = 0
                for (name, email) in (self.mailVerteiler):
                    notify(f'{name}: {email}')
                    if email:
                        emailCounter += 1
                notify('Insgesamt {} Empfänger, davon {} mit eMail-Adresse.'.format(
                    len(self.mailVerteiler),
                    emailCounter
                    ), 'Hinweis')
            
            def sendebericht():
                #
                # Sendebericht anlegen und füllen
                Sendebericht = {}
                Sendebericht['Email'] = glb.aktuelleGemeinde['mail_from']
                jetzt = datetime.datetime.now().strftime('%d.%m.%Y %H:%M')
                Sendebericht['Betreff'] = f'Sendebericht eMail-Versand {jetzt}'
                for feld in ('P_ID', 'Name', 'Vorname',
                          'Bcc', 'Strasse', 'PLZ', 'Ort', 'Land',
                          'Anrede', 'Anhang'):
                    Sendebericht[feld] = None
                Sendebericht['Text'] = f'Sendebericht zum eMail-Versand vom {jetzt}\n\n'
                #
                # Gruppen und Versandarten aufbereiten
                gruppen = glb.formMailVersand.getValue('gruppen')
                if gruppen is None:
                    gruppen = []
                elif type(gruppen) != list:
                    gruppen = [gruppen,]
                versandarten = glb.formMailVersand.getValue('versandarten')
                if versandarten is None:
                    versandarten = []
                elif type(versandarten) != list:
                    versandarten = [versandarten,]
                gruppenListe = ', '.join([f"'{gr}'" for gr in gruppen])
                versandartenListe = ', '.join([f"'{va}'" for va in versandarten])
                Sendebericht['Text'] += f'Gruppen:      {gruppenListe}\n'
                Sendebericht['Text'] += f'Versandarten: {versandartenListe}\n'
                #
                # Absender
                Absender = {}
                for key in ['mail_from', 'mail_reply',
                        'smtp_server', 'smtp_port',
                        'smtp_user', 'smtp_password']:
                    Absender[key] = glb.aktuelleGemeinde[key]
                Absender['email'] = glb.aktuelleGemeinde['mail_from']
                Absender['reply'] = glb.aktuelleGemeinde['mail_reply']
                #
                # Sendebericht verschicken
                if not MailOderBrief(Sendebericht, Absender):
                    notify('Sendebericht gescheitert', 'Warnung')
            
            def handleMailSend():
                """handleMailSend - Verschickt die eMail an den Verteiler
                
                """
                notify('=======================================')
                notify('Mail Versand')
                notify('=======================================')
                #
                # Wenn kein Betreff, dann Abbruch
                betreff = glb.formMailVersand.getValue('betreff')
                if not betreff:
                    notify('Abbruch: Kein Betreff angegeben.', 'Warnung')
                    return
                #
                # Verteiler aufbauen
                self.mailVerteiler = getMailVerteiler()
                #
                # Verteiler ggf. um Absender für die Beleg-Mail ergänzen
                if glb.formMailVersand.getValue('beleg'):
                    self.mailVerteiler.append(('Beleg-Mail', glb.aktuelleGemeinde['mail_from']))
                #
                # Absender und Brief (bzw. erst einmal Mail) zusammensetzen,
                # soweit für alle Empfänger gleich
                Brief = {}
                Brief['P_ID'] = ''
                # Ggf. vergewissern, ob wirklich jede einzelne Mail protokolliret werden soll
                if glb.formMailVersand.getValue('protokoll'):
                    if not dialog.askokcancel(
                            title='Weiter mit Bcc',
                            message=MAIL_WITH_BCC_MESSAGE
                            ):
                        Brief['Bcc'] = None
                        glb.formMailVersand.setValue('protokoll', False)
                        notify('Abbruch, da Protokollmail doch nicht gewünscht.', 'Warnung')
                        return
                    Brief['Bcc'] = glb.aktuelleGemeinde['mail_from']
                else:
                    Brief['Bcc'] = None
                Brief['Betreff'] = glb.formMailVersand.getValue('betreff')
                Brief['Text'] = glb.formMailVersand.getValue('nachricht')
                Brief['Anhang'] = [pfad for (pfad, basename) in self.mailAttachments]
                Absender = {}
                for key in ['mail_from', 'mail_reply',
                        'smtp_server', 'smtp_port',
                        'smtp_user', 'smtp_password']:
                    Absender[key] = glb.aktuelleGemeinde[key]
                #
                # Zähler und Anzahl für Anzeige des Fortgangs
                anzahl = len(self.mailVerteiler)
                count = 0
                #
                # Verteiler durchgehen
                for (name, mail) in self.mailVerteiler:
                    count += 1
                    logTextFortgang = f'{count:>3} von {anzahl:>3}:'
                    if mailAdresse := mail.strip():
                        # Nur, wenn es eine eMail-Adresse gibt
                        Brief['Name'] = name
                        Brief['Vorname'] = ''
                        Brief['Email'] = mailAdresse
                        Brief['Strase'] = ''
                        Brief['PLZ'] = ''
                        Brief['Ort'] = ''
                        Brief['Land'] = ''
                        Brief['Anrede'] = ''
                        Absender['strasse'] = glb.aktuelleGemeinde['strasse']
                        Absender['plz'] = glb.aktuelleGemeinde['plz']
                        Absender['ort'] = glb.aktuelleGemeinde['ort']
                        Absender['land'] = glb.aktuelleGemeinde['land']
                        Absender['land_kurz'] = glb.aktuelleGemeinde['land_kurz']
                        Absender['email'] = glb.aktuelleGemeinde['mail_from']
                        Absender['reply'] = glb.aktuelleGemeinde['mail_reply']
                        if MailOderBrief(Brief, Absender):
                            notify(f'{logTextFortgang} OK: {name}', 'Erfolg')
                        else:
                            notify(f'{logTextFortgang} Fehler: {name}', 'Fehler')
                    else:
                        notify(f'{logTextFortgang} übersprungen, keine eMail-Adr.: {name}', 'Warnung')
                #
                # Sendebericht verschicken und Abschluss melden
                sendebericht()
                notify('Mail Versand abgeschlossen')
            
            def handleMailReset():
                """handleMailReset - Reagiert auf Button Reset
                """
                resetMail()
            
            def getMailVerteiler():
                """getMailVereiler - Baut den Verteiler für den Mail Versand auf
                
                    Baut den Mail-Verteiler aus den ggf. ausgewählten Gruppen und Versandarten
                    auf. Dabei wird folgende Logik implementiert, d.h. es werden folgende
                    Personen und Familien (P/F) in den Verteiler aufgenommen:
                        1. Keine Gruppen und keine Versandarten ausgewählt
                              Alle P/F, die eine eMail-Adresse haben
                        2. Gruppen, aber keine Versandarten ausgewählt
                              Alle P/F, die mindestens zu einer der ausgewählten Gruppen gehören
                        3. Versandarten, aber keine Gruppen ausgewählt
                              Alle P/F, die mindestens eine der ausgewählten Versandarten haben
                        4. Sowohl Gruppen als auch Versandarten ausgewählt
                              Alle P/F, die mindestens zu einer der ausgewählten Gruppen gehören und
                              außerdem mindestens eine der ausgewählten Versandarten haben
                    
                    Wir realisieren das über eine SQL-Abfrage (also nicht über die Modelle).
                    
                    Ergebnis
                        Liste von Tupeln
                            [(name, email), ...]
                """
                #
                # Verlauf zeigen
                notify('Passende eMail-Adressen suchen...')
                #
                # Gruppen und Versandarten
                gruppen = glb.formMailVersand.getValue('gruppen')
                if gruppen is None:
                    gruppen = []
                elif type(gruppen) != list:
                    gruppen = [gruppen,]
                versandarten = glb.formMailVersand.getValue('versandarten')
                if versandarten is None:
                    versandarten = []
                elif type(versandarten) != list:
                    versandarten = [versandarten,]
                gruppenListe = ', '.join([f"'{gr}'" for gr in gruppen])
                versandartenListe = ', '.join([f"'{va}'" for va in versandarten])
                #
                # Fallunterscheidung für obige Logik
                # Dabei werden die where-Klauseln whereF und whereP (für Fmilien bzw. Personen)
                # gebaut, die später in die SQL-Abfrage eingebaut werden.
                if gruppen or versandarten:
                    # Fall 2, 3, 4
                    if gruppen and versandarten:
                        # Fall 4
                        whereP = """where
                            exists (
                                select * from {Schema}.tbl_person_gruppe as pg
                                where
                                    pg.person_id = p.id
                                    and pg.gruppe_kurz_bez in ({gruppen})
                                )
                            and exists (
                                select * from {Schema}.tbl_person_versandart as pv
                                where
                                    pv.person_id = p.id
                                    and pv.versandart in ({versandarten})
                                )
                        """.format(
                                Schema=glb.aktuelleGemeinde['schema'],
                                gruppen=gruppenListe,
                                versandarten=versandartenListe)
                        whereF = """where
                            exists (
                                select * from {Schema}.tbl_familie_gruppe as fg
                                where
                                    fg.familie_id = f.id
                                    and fg.gruppe_kurz_bez in ({gruppen})
                                )
                            and exists (
                                select * from {Schema}.tbl_familie_versandart as fv
                                where
                                    fv.familie_id = f.id
                                    and fv.versandart in ({versandarten})
                                )
                        """.format(
                                Schema=glb.aktuelleGemeinde['schema'],
                                gruppen=gruppenListe,
                                versandarten=versandartenListe)
                    elif gruppen:
                        # Fall 2
                        whereP = """where
                            exists (
                                select * from {Schema}.tbl_person_gruppe as pg
                                where
                                    pg.person_id = p.id
                                    and pg.gruppe_kurz_bez in ({gruppen})
                                )
                        """.format(
                                Schema=glb.aktuelleGemeinde['schema'],
                                gruppen=gruppenListe)
                        whereF = """where
                            exists (
                                select * from {Schema}.tbl_familie_gruppe as fg
                                where
                                    fg.familie_id = f.id
                                    and fg.gruppe_kurz_bez in ({gruppen})
                                )
                        """.format(
                                Schema=glb.aktuelleGemeinde['schema'],
                                gruppen=gruppenListe)
                    elif versandarten:
                        # Fall 3
                        whereP = """where
                            exists (
                                select * from {Schema}.tbl_person_versandart as pv
                                where
                                    pv.person_id = p.id
                                    and pv.versandart in ({versandarten})
                                )
                        """.format(
                                Schema=glb.aktuelleGemeinde['schema'],
                                versandarten=versandartenListe)
                        whereF = """where
                            exists (
                                select * from {Schema}.tbl_familie_versandart as fv
                                where
                                    fv.familie_id = f.id
                                    and fv.versandart in ({versandarten})
                                )
                        """.format(
                                Schema=glb.aktuelleGemeinde['schema'],
                                versandarten=versandartenListe)
                    else:
                        # Panik
                        raise Exception('Panik: dieser Fall darf nicht eintreten.')
                else:
                    # Fall 1
                    whereP = ''
                    whereF = ''
                sql = """
                    select
                        name || ', ' || vorname as name,
                        email
                    from
                        {Schema}.tbl_person as p
                    {whereP}
                    union select
                        name,
                        email
                    from
                        {Schema}.tbl_familie as f
                    {whereF}
                    order by
                        name
                    """.format(Schema=glb.aktuelleGemeinde['schema'], whereP=whereP, whereF=whereF)
                with glb.DB.cursor() as cur:
                    cur.execute(sql)
                    zeilen = cur.fetchall()
                    ergebnis = [(name, email) for (name, email) in zeilen]
                    glb.DB.commit()
                notify('... OK', 'Erfolg')
                return ergebnis
            def resetMail():
                """resetMail - Setzt alle Werte auf Defaults
                """
                signature = glb.aktuelleGemeinde['mail_signatur']
                glb.formMailVersand.setValue(
                    'nachricht',
                    '\n\n\n' + signature
                    )
                glb.formMailVersand.nachricht.mark_set("insert", "0.0")
                glb.formMailVersand.setValue('betreff', '')
                glb.formMailVersand.setValue('gruppen', None)
                glb.formMailVersand.setValue('anhang', '')
                glb.formMailVersand.setValue('versandarten', None)
                glb.formMailVersand.setValue('beleg', True)
                glb.formMailVersand.setValue('protokoll', False)
            #
            # Frames für Nachricht und Steuerung bauen und einsetzen
            self.frmMail = ttk.LabelFrame(
                self.frmMailVersand,
                text='E-Mail')
            self.frmMail.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
            #
            self.frmMailSteuerung = ttk.LabelFrame(
                self.frmMailVersand,
                text='Verteiler')
            self.frmMailSteuerung.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
            #
            self.frmMailGruppen = ttk.LabelFrame(
                self.frmMailSteuerung,
                text='Gruppen')
            self.frmMailGruppen.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
            #
            self.frmMailVersandarten = ttk.LabelFrame(
                self.frmMailSteuerung,
                text='Versandarten')
            self.frmMailVersandarten.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
            #
            self.frmMailKontrolle = ttk.LabelFrame(
                self.frmMailSteuerung,
                text='Versand-Kontrolle')
            self.frmMailKontrolle.pack(side=tk.TOP, expand=True, fill=tk.X)
            #
            self.frmMailButtons = ttk.LabelFrame(
                self.frmMailSteuerung,
                text='Aktionen')
            self.frmMailButtons.pack(side=tk.TOP, expand=True, fill=tk.X)
            #
            # Widgets herstellen, zeigen und in Formular aufnehmen
            form.addWidget(
                'betreff',
                ttk.Entry(self.frmMail),
                'text',
                label='Betreff')
            form.lbl_betreff.pack(side=tk.TOP, anchor=tk.W)
            form.betreff.pack(side=tk.TOP, expand=True, fill=tk.X, anchor=tk.W)
            
            form.addWidget(
                'nachricht',
                scrolledtext.ScrolledText(self.frmMail),
                'text',
                label=ttk.Label(self.frmMail, text='Nachricht'))
            form.lbl_nachricht.pack(side=tk.TOP, anchor=tk.W)
            form.nachricht.pack(side=tk.TOP, expand=True, fill=tk.BOTH, anchor=tk.W)
            
            form.addWidget(
                'anhang',
                ttk.Label(self.frmMail),
                'text',
                label='Anhänge')
            form.lbl_anhang.pack(side=tk.TOP, anchor=tk.W)
            form.anhang.pack(side=tk.TOP, expand=True, fill=tk.X, anchor=tk.W)
            
            self.frmMailAnhangButtons = ttk.Frame(self.frmMail)
            self.frmMailAnhangButtons.pack(side=tk.TOP, expand=True, fill=tk.X)
                
            self.btnAnhang = ttk.Button(
                self.frmMailAnhangButtons,
                text='Anhänge auswählen',
                image=glb.icons.getIcon('search'),
                compound=tk.LEFT,
                command=handleMailAnhang
                )
            self.btnAnhang.pack(side=tk.LEFT, expand=True, fill=tk.X)
            
            self.btnAnhangClear = ttk.Button(
                self.frmMailAnhangButtons,
                text='Anhänge entfernen',
                image=glb.icons.getIcon('delete'),
                compound=tk.LEFT,
                command=handleMailAnhangClear
                )
            self.btnAnhangClear.pack(side=tk.LEFT, expand=True, fill=tk.X)
            
            form.addWidget(
                'gruppen',
                FrameScrolledListboxValueLabel(
                    self.frmMailGruppen),
                'text'
                )
            form.gruppen.Listbox.config(selectmode=tk.MULTIPLE)
            form.setGetterAuswahl(
                  'gruppen',
                  PersonGruppeSchlank().FactoryGetterChoices('gruppe_kurz_bez'))
            form.gruppen.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
            
            form.addWidget(
                'versandarten',
                FrameScrolledListboxValueLabel(
                    self.frmMailVersandarten),
                'text'
                )
            form.versandarten.Listbox.config(selectmode=tk.MULTIPLE)
            form.setGetterAuswahl(
                  'versandarten',
                  PersonVersandartSchlank().FactoryGetterChoices('versandart'))
            form.versandarten.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
            
            form.addWidget(
                'beleg',
                ttk.Checkbutton(self.frmMailKontrolle),
                'bool',
                label='Beleg-Mail'
                )
            form.beleg.pack(side=tk.LEFT)
            form.lbl_beleg.pack(side=tk.LEFT)
                        
            ttk.Separator(self.frmMailKontrolle, orient=tk.VERTICAL).pack(
                    side=tk.LEFT, fill=tk.Y)
            
            form.addWidget(
                'protokoll',
                ttk.Checkbutton(self.frmMailKontrolle),
                'bool',
                label='Protokoll-Mail'
                )
            form.protokoll.pack(side=tk.LEFT)
            form.lbl_protokoll.pack(side=tk.LEFT)
            
            self.btnCheck = ttk.Button(
                self.frmMailButtons,
                text='Check',
                image=glb.icons.getIcon('check'),
                compound=tk.LEFT,
                command=handleMailCheck
                )
            self.btnCheck.pack(side=tk.LEFT)
            
            self.btnSend = ttk.Button(
                self.frmMailButtons,
                text='Senden',
                image=glb.icons.getIcon('send'),
                compound=tk.LEFT,
                command=handleMailSend
                )
            self.btnSend.pack(side=tk.LEFT)
            
            self.btnReset = ttk.Button(
                self.frmMailButtons,
                text='Zurücksetzen',
                image=glb.icons.getIcon('refresh'),
                compound=tk.LEFT,
                command=handleMailReset
                )
            self.btnReset.pack(side=tk.LEFT)
    
        #
        # Etiketten
        with Form() as form:
            glb.formEtiketten = form
            #
            # Methoden - Button Handler
            def handleEtikettenStart():
                #
                # Job herstellen
                job = Jobs()
                #
                # Kommandozeilen Parameter
                cl_user = '-u {}'.format(glb.PSQL_USER)
                gruppen = glb.formEtiketten.getValue('gruppen')
                if gruppen is None:
                    gruppen = []
                elif type(gruppen) != list:
                    gruppen = [gruppen,]
                if gruppen:
                    cl_gruppen = '-g ' + ' '.join(gruppen)
                else:
                    cl_gruppen = ''
                versandarten = glb.formEtiketten.getValue('versandarten')
                if versandarten:
                    cl_versandarten = '-v ' + ' '.join(versandarten)
                else:
                    cl_versandarten = ''
                gemeinde = glb.aktuelleGemeinde
                cl_absender = ''
                if glb.formEtiketten.getValue('absender'):
                    absender = gemeinde['kurz_bez']
                    if 'CG' in absender or 'Christengemeinschaft' in absender:
                        absender = 'Die Christengemeinschaft'
                    absender += ' -- '
                    absender += '{}, {} {}'.format(gemeinde['strasse'], gemeinde['plz'], gemeinde['ort'])
                    cl_absender = f'-a "{absender}"'
                cl_schema = '-s {}'.format(gemeinde['schema'])
                job.titel = 'Gemeinde: Etiketten'
                job.kommando = 'Ge-14-Etiketten.py {} {} {} {} {}'.format(
                    cl_user, cl_schema, cl_gruppen, cl_versandarten, cl_absender)
                logger.debug(f'Kommando: {job.kommando}')
                job.verzeichnis = '/home/ulrich/Python/'
                job.beschreibung = ''
                job.intervall = 1
                job.einheit = 'ta'
                job.sofort = True
                job.aktiv = True
                job.gestoppt = False
                job.selbstzerstoerend = True
                id = job.save()
                logger.debug(f'Erfolgreich gespeichert: {id=}')
                notify(f'Job für Etiketten erfolgreich auf den Weg gebracht: {id=}', 'Erfolg')
                
            #
            # Widgets herstellen und einfügen
            form.addWidget(
                'gruppen',
                FrameScrolledListboxValueLabel(
                    self.frmEtiketten),
                'text',
                label='Gruppen'
                )
            form.gruppen.Listbox.config(selectmode=tk.MULTIPLE)
            form.setGetterAuswahl(
                  'gruppen',
                  PersonGruppeSchlank().FactoryGetterChoices('gruppe_kurz_bez'))
            form.lbl_gruppen.grid(column=0, row=0, sticky=tk.W)
            form.gruppen.grid(column=0, row=1, sticky=tk.W)
                        
            form.addWidget(
                'versandarten',
                FrameScrolledListboxValueLabel(
                    self.frmEtiketten),
                'text',
                label='Versandarten'
                )
            form.versandarten.Listbox.config(selectmode=tk.MULTIPLE)
            form.setGetterAuswahl(
                  'versandarten',
                  PersonVersandartSchlank().FactoryGetterChoices('versandart'))
            form.lbl_versandarten.grid(column=1, row=0, sticky=tk.W)
            form.versandarten.grid(column=1, row=1, sticky=tk.W)
            
            form.addWidget(
                'absender',
                ttk.Checkbutton(self.frmEtiketten),
                'bool',
                label='Absender einfügen'
                )
            form.absender.grid(column=2, row=0, sticky=tk.E)
            form.lbl_absender.grid(column=3, row=0, sticky=tk.W)
            
            self.btnEtikettenStart = ttk. Button(
                self.frmEtiketten,
                text='Etiketten herstellen',
                image=glb.icons.getIcon('pdf'),
                compound=tk.LEFT,
                command=handleEtikettenStart
                )
            self.btnEtikettenStart.grid(column=2, row=1, columnspan=2, sticky=tk.W+tk.S)
    
    def disableMainNotebook(self):
        """disableMainNotebook - Deaktiviert alle Tabs des Main Notebook
        """
        for index in range(self.nbkMain.index(tk.END)):
            self.nbkMain.tab(index, stat=tk.DISABLED)
                        
    def enableMainNotebook(self):
        """enableMainNotebook - Aktiviert alle Tabs des Main Notebook
        """
        for index in range(self.nbkMain.index(tk.END)):
            self.nbkMain.tab(index, stat=tk.NORMAL)
                        
    def baueLayout(self):
        #
        # Kopfleiste
        self.frmTop = ttk.Frame(self)
        self.frmTop.pack()
        #
        # Paned Window für Haupt und Fuß Frame
        self.pndHauptUndFuss = ttk.PanedWindow(self, orient=tk.VERTICAL)
        self.pndHauptUndFuss.pack(expand=tk.YES, fill=tk.BOTH)
        #
        # Haupt Frame
        self.frmMain = ttk.Frame(self.pndHauptUndFuss)
        self.pndHauptUndFuss.add(self.frmMain)
        #
        # Fuß Frame
        self.frmBottom = ttk.Frame(self.pndHauptUndFuss)
        self.pndHauptUndFuss.add(self.frmBottom)
        #
        # Haupt-Notebook
        self.nbkMain = ttk.Notebook(self.frmMain)
        self.nbkMain.pack(expand=tk.YES, fill=tk.BOTH)
        #
        # Unter-Notebooks
        self.frmNbkPersonen = ttk.Frame(self.frmMain)
        self.nbkMain.add(self.frmNbkPersonen, text='Personen')
        self.nbkPersonen = ttk.Notebook(self.frmNbkPersonen)
        self.nbkPersonen.pack(expand=tk.YES, fill=tk.BOTH)
        
        self.frmNbkFamilien = ttk.Frame(self.frmMain)
        self.nbkMain.add(self.frmNbkFamilien, text='Familien')
        self.nbkFamilien = ttk.Notebook(self.frmNbkFamilien)
        self.nbkFamilien.pack(expand=tk.YES, fill=tk.BOTH)
        
        self.frmNbkHelferlein = ttk.Frame(self.frmMain)
        self.nbkMain.add(self.frmNbkHelferlein, text='Helferlein')
        self.nbkHelferlein = ttk.Notebook(self.frmNbkHelferlein)
        self.nbkHelferlein.pack(expand=tk.YES, fill=tk.BOTH)
        
        self.frmNbkAktionen = ttk.Frame(self.frmMain)
        self.nbkMain.add(self.frmNbkAktionen, text='Aktionen')
        self.nbkAktionen = ttk.Notebook(self.frmNbkAktionen)
        self.nbkAktionen.pack(expand=tk.YES, fill=tk.BOTH)
        
        self.frmNbkVerwaltung = ttk.Frame(self.frmMain)
        self.nbkMain.add(self.frmNbkVerwaltung, text='Verwaltung')
        self.nbkVerwaltung = ttk.Notebook(self.frmNbkVerwaltung)
        self.nbkVerwaltung.pack(expand=tk.YES, fill=tk.BOTH)
        #
        # Frames in Notebooks
        self.frmPersonenEinzelheiten = ttk.Frame(self.frmNbkPersonen)
        self.nbkPersonen.add(self.frmPersonenEinzelheiten, text='Einzelheiten')
        
        self.frmPersonenListe = ttk.Frame(self.frmNbkPersonen)
        self.nbkPersonen.add(self.frmPersonenListe, text='Als Liste')
        
        self.frmFamilienEinzelheiten = ttk.Frame(self.frmNbkFamilien)
        self.nbkFamilien.add(self.frmFamilienEinzelheiten, text='Einzelheiten')
        
        self.frmFamilienListe = ttk.Frame(self.frmNbkFamilien)
        self.nbkFamilien.add(self.frmFamilienListe, text='Als Liste')
        
        self.frmGruppenEinzelheiten = ttk.PanedWindow(
            self.frmNbkHelferlein,
            orient=tk.HORIZONTAL)
        self.nbkHelferlein.add(self.frmGruppenEinzelheiten, text='Gruppen')
        
        self.frmGruppenListe = ttk.Frame(self.frmNbkHelferlein)
        self.nbkHelferlein.add(self.frmGruppenListe, text='Gruppen als Liste')
        self.frmGruppenListeNavi = ttk.Frame(self.frmGruppenListe)
        self.frmGruppenListeInhalt = yScrolledFrame(self.frmGruppenListe)
        self.frmGruppenListeNavi.pack(
            side=tk.TOP,
            anchor=tk.W,
            )
        self.frmGruppenListeInhalt.pack(
            side=tk.TOP,
            expand=tk.YES,
            fill=tk.BOTH
            )
        
        self.frmVersandartenEinzelheiten = ttk.PanedWindow(
            self.frmNbkHelferlein,
            orient=tk.HORIZONTAL)
        self.nbkHelferlein.add(self.frmVersandartenEinzelheiten, text='Versandarten')
        
        self.frmAnredenEinzelheiten = ttk.PanedWindow(
            self.frmNbkHelferlein,
            orient=tk.HORIZONTAL)
        self.nbkHelferlein.add(self.frmAnredenEinzelheiten, text='Anreden')
        
        self.frmMailVersand = ttk.Frame(self.frmNbkAktionen)
        self.nbkAktionen.add(self.frmMailVersand, text='eMail-Versand')
        
        self.frmEtiketten = ttk.Frame(self.frmNbkAktionen)
        self.nbkAktionen.add(self.frmEtiketten, text='Etiketten')
        
        self.frmFarbenEinzelheiten = ttk.PanedWindow(
            self.frmNbkVerwaltung,
            orient=tk.HORIZONTAL)
        self.nbkVerwaltung.add(self.frmFarbenEinzelheiten, text='Farben')

        self.frmGemeindenEinzelheiten = ttk.PanedWindow(
            self.frmNbkVerwaltung,
            orient=tk.HORIZONTAL)
        self.nbkVerwaltung.add(self.frmGemeindenEinzelheiten, text='Gemeinden')
        
        self.frmJobsEinzelheiten = ttk.PanedWindow(
            self.frmNbkVerwaltung,
            orient=tk.HORIZONTAL)
        self.nbkVerwaltung.add(self.frmJobsEinzelheiten, text='Reg. Aufgaben')
        
        self.frmJobsListe = ttk.Frame(self.nbkVerwaltung)
        self.nbkVerwaltung.add(self.frmJobsListe, text='Reg. Aufg. a. Liste')
        self.frmJobsListeNavi = ttk.Frame(self.frmJobsListe)
        self.frmJobsListeInhalt = yScrolledFrame(self.frmJobsListe)
        self.frmJobsListeNavi.pack(
            side=tk.TOP,
            anchor=tk.W)
        self.frmJobsListeInhalt.pack(
            side=tk.TOP,
            expand=tk.YES,
            fill=tk.BOTH)

def main():
    configuration()
    
    hauptprogramm = Hauptprogramm()
    hauptprogramm.mainloop()

if __name__ == '__main__':
    main()
