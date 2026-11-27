# Makroschliff-Aufbereitung

Windows-Programm zum Aufbereiten von **echten** Handyfotos geätzter Makroschliffe
(Schweißverbindungen) für die Auftragsdokumentation – inklusive Einzeichnen von
Schmelzlinie, Lagengrenzen, Raupennummern und Maßen.

Das Programm bearbeitet ausschließlich das aufgenommene Foto (Helligkeit, Kontrast,
Schärfe). Es werden **keine Bildinhalte erzeugt, hinzugefügt oder entfernt**.
Der Export enthält auf Wunsch den unbearbeiteten Original-Ausschnitt und einen
Hinweis auf die angewendeten Bearbeitungsschritte.

## Download

**[⬇ Makroschliff.exe – aktuelle Version](https://github.com/Bertileinchen/MakroMaster/releases/latest/download/Makroschliff.exe)**

Dieser Link liefert immer die neueste Version. Ältere Versionen und Änderungen:
[Releases](https://github.com/Bertileinchen/MakroMaster/releases).
Keine Installation nötig – einfach starten. Alle Daten bleiben auf dem Rechner.
Die installierte Version steht im Programm links oben.

Voraussetzung: Windows 10/11 mit *Microsoft Edge WebView2 Runtime*
(auf aktuellen Windows-Rechnern vorhanden).

## Ablauf

1. **Foto laden** – Button oder per Drag & Drop.
2. **Ausrichten & Zuschneiden** – Probe waagrecht drehen, Rechteck aufziehen.
3. **Probe freistellen** – rund um die Probe klicken (an jeder Ecke ein Punkt);
   dazwischen folgt die Kontur automatisch der Probenkante (Live-Wire).
4. **Aufbereitung** – `Auto` sucht die Einstellung, bei der Schmelz- und
   Lagengrenzen am deutlichsten werden; danach von Hand nachregeln.
5. **Einzeichnen** – Schmelzlinie / Lagengrenze (folgt der Kante), Raupennummern,
   Maße, Text. `Kalibrieren`: zwei Punkte mit bekanntem Abstand (Maßband,
   Blechdicke) → Maße in mm und Maßstabsbalken.
6. **Schriftfeld & Export** – PNG mit Schriftfeld, Original-Ausschnitt und
   Bearbeitungshinweis.

Tastatur: `O` (halten) = Original zeigen, `F` = einpassen, `Strg+Z` = rückgängig,
`Enter` = Linie/Kontur abschließen, `Esc` = abbrechen, `Entf` = Auswahl löschen,
Leertaste + Ziehen = verschieben, Mausrad = Zoom.

## Fototipps

- Licht flach von der Seite, kein Blitz. Spiegelungen vom nassen Schliff
  zerstören Bildinformation (Option „Überbelichtete Stellen rot markieren“).
- Polfilter: Folie vor Lampe + Filter vor Kamera, 90° gegeneinander gedreht
  (Kreuzpolarisation).
- Handy auf Stativ/aufgelegt, wenn möglich Pro-Modus ohne HDR.

## Entwicklung

```
pip install -r requirements.txt
python makroschliff.py            # startet das Fenster
python makroschliff.py --debug    # mit Entwicklerwerkzeugen
```

Die Oberfläche liegt komplett in `app/index.html` (HTML/JavaScript, ohne externe
Abhängigkeiten) und lässt sich auch direkt im Browser öffnen.

### EXE bauen

Automatisch per GitHub Actions (`.github/workflows/build.yml`): Jeder Push auf
`main` baut die EXE und veröffentlicht sie als neues Release
`v<VERSION>.<Build-Nr.>` (z. B. `v1.0.7`). Der Download-Link oben zeigt
automatisch auf das neueste. Für einen größeren Versionssprung die Zahl in der
Datei `VERSION` ändern (z. B. `1.1`).

Lokal unter Windows:

```
pip install -r requirements.txt pyinstaller
pyinstaller --onefile --windowed --name Makroschliff --icon assets/icon.ico --add-data "app;app" makroschliff.py
```
