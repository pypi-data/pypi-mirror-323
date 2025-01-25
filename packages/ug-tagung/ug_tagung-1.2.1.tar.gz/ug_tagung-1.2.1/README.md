# ug_tagung.Tagung

Verwaltung für Tagungen.


## Abkürzungen

| Abk. | Ausgeschrieben |
| ---- | -------------- |
| DB   | Datenbank      |
| TB   | Tagungsbüro    |
| TN   | Teilnehmer     |
| VA   | Veranstaltung  |
| WS   | Workshop       |


## Features

* **Verwaltung der Personen Daten**
    * Kontaktdaten
    * Anmeldestatus
    * Bezahlung
* **Verwaltung von Institutions-Daten**
    * Unter Institutionen verstehen wir Firmen, Schulen, Gemeinden usw., also eigentlich alle
    Kontakte, die keine Personen sind, aber etwas mit der Tagung zu tun haben.
    * Es werden im Wesentlichen Kontaktdaten verwaltet.
    * Institutionen können beim Quartier-Management wichtig werden. Siehe dazu weiter unten.
* **Anmelde-Logistik**
    * Online-Anmeldungen werde automatisch in die Datenbank eingefügt
    * Über den Anmeldestatus steuert das TB Bestätigungs* und andere Mails an die TN
* **WS-Logistik**
    * Halbautomatische Zuordnung der WS-Anmeldungen zu den bereits angemeldeten TNn
    * Aussagekräftige Arbeitslisten zur tatsächlichen Zuteilung der TN auf die WSs. Das ist nötig, da die WS-Anmeldungen 1., 2. und 3. Wahl kennen und keine vollautomatische Zuteilung gewünscht ist.
    * TN-Listen für die WSs
    * Es können bis zu 4 unterschiedliche Arten von WSs unabhängig voneinander verwaltet werden. Z.B. könnte es vormittags Gesprächsgruppen und nachmittags künstlerische und sportliche Workshops geben.
* **Gruppen (= Rollen)**
    * Jede Person in der DB kann einer oder mehreren Gruppen angehören. Typische Gruppen sind:
        * TN = Teilnehmer
        * Doz = Dozent
        * Team = Tagungsteam (Vorbereitung und Durchführung)
        * Pr = Priester
    * Es können beliebig weitere Gruppen definiert werden.
* **Veranstaltungs- und Raum-Management**
    * Bei Bedarf (d.h. z.B. Tagungen mit mehr als 300 TN oder mehr als 50 VAen) können sämtliche VAen und alle verfügbaren Räume (incl. Außenflächen u.a.). Später können jeder VA eine oder mehrere Zeiten in den Räumen zugewiesen werden. Die vorhandenen Daten werden ausgewertet zu:
    * Studenplänen für jeden Raum bzw. für jede VA.
    * In den Stundenplänen werden Überschneidungen (= Doppelbelegungen) farblich signalisiert.
* **TN-Listen und andere PDF-Auswertungen**
    * TN-Liste und alle anderen PDF-Auswertungen werden regelmäßig und in einstellbaren Intervallen automatisch erzeugt und über eine NextCloud zur Ansicht und zum Download bereitgestellt.
    * Zu den möglichen Auswertungen gehören:
        * TN-Gesamtliste
        * Gruppenlisten (d.h. für jede Gruppe eine Liste)
        * Statistik (Überblick über Anmeldungen, zugesagte TN-Beiträge u.a.
    * Die TN-Liste ist so konzipiert, dass sie zu Beginn der Tagung beim Empfang (Counter) alle relevanten Informationen übersichtlich zeigt, s.d. nötigenfalls gezielt Unklarheiten mit dem TN geklärt werden können. Insb. gehört dazu, ob der TN-Beitrag in der zu erwartenden Höhe bereits gezahlt wurde.
* **Quartier-Management**
    * Personen und Instituionen können "Quartiergeber" werden, indem sie ein oder mehrere Quartiere anbieten. Von der Couch im Wohnzimmer bis zum Hotelzimmer ist alles möglich.
    * Andere Personen können in solchen Quartieren untergebracht werden.
    * Diese Unterbringungen werden in den Auswertungen mit ausgegeben.

Das Programm wurde und wird von Ulrich Goebel speziell für die Anforderungen von kirchlichen Tagungen entwickelt.

Das hier verfügbare Paket beinhaltet ausschließlich die GUI für diese Adressverwaltung. Die Daten werden in einer PostgreSQL-Datenbank gehalten, die auf einem eigenen Server läuft. Auswertungen, also PDFs zum Ausdrucken von Adresslisten u.a. werden ebenso auf diesem Server durch einen Cron-Job regelmäßig hergestellt und über eine Nextcloud bereitgestellt.

Durch die spezielle Architektur ist das Paket kaum für jedermann brauchbar. Falls es aber Interesse gibt, kann man sich gerne an Ulrich Goebel wenden (ulrich@fam-goebel.de).


# Systemvoraussetzungen

* Linux (empfohlen), Windows oder Mac
* Python 3
* Oxygen Icons installiert


# Installation

## Linux

### Python

In aller Regel ist auf Linux-Systemen Python 3 installiert. Falls nicht, muss man es über die üblichen Repositories nachholen.

#### Virtual Environment

Es wird dringend empfohlen (und im Folgenden vorausgesetzt), die GUI innerhalb einer Virtuellen Umgebung laufen zu lassen. Dafür:

1. Ein Verzeichnis für die GUI anlegen, z.B.  
`mkdir Tagung`
2. Dort eine virtuelle Umgebung anlegen:  
`cd Tagung`  
`python3 -m venv .venv`  
Damit wird innerhalb des Verzeichnisses `Tagung` eine Virtuelle Umgebung namens `.venv` angelegt.
2. Die Virtuelle Umgebung aktivieren:  
`. .venv/bin/activate`
3. Die GUI installieren * siehe unten
4. Nach Beendigung der Arbeit die Virtuelle Umgebung deaktivieren:  
`deactivate`

### Oxygen Icons

Unter Linux (z.B. Ubuntu) stehen die Oxygen Icons i.d.R. als Paket zur Verfügung: `oxygen-icon-theme`

### ug_tagung.Tagung


