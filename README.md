# KognitivTrainer

Android-App mit **500 Aufgaben** zum Trainieren von Kopf und Reaktion – komplett offline, alle Ergebnisse bleiben auf dem Handy.

## Download

Die fertige APK wird bei jeder Änderung automatisch von GitHub gebaut:

**https://github.com/xlsolutionnorth-pixel/KognitivTrainer/releases/latest/download/KognitivTrainer.apk**

Auf dem Handy öffnen, herunterladen und installieren (beim ersten Mal „Installation aus unbekannten Quellen“ erlauben).

## Inhalt

| Bereich | Anzahl | Aufgaben |
|---|---|---|
| 🧮 Rechnen & Logik | 160 | Kopfrechnen, Prozent, Brüche, Gleichungen, Zahlenreihen, Logikrätsel, Textaufgaben |
| 📐 Geometrie & Raum | 120 | Fläche & Umfang, Winkel, Pythagoras, Körper, mentale Rotation, Spiegelbilder, Koordinaten |
| 🧠 Gedächtnis & Aufmerksamkeit | 120 | Zahlen merken (vor-/rückwärts), Farbfolgen, Wörter merken, Positionen merken, Stroop-Test, „Finde das Andere“, Symbole zählen |
| ⚡ Reaktion & Tempo | 100 | Reaktionstest, Go/No-Go, Pfeil-Richtung (Flanker), schneller Vergleich, Schulte-Tabelle, Ziele treffen, Rechen-Sprint |

Jede Aufgabe hat eine Stufe (leicht / mittel / schwer) und eine Erklärung, die nach dem Lösen angezeigt wird.

## Funktionen

- **Tägliches Training**: jeden Tag 10 Aufgaben aus allen Bereichen, mit Serie (🔥)
- **Zufallsmix** und **Schwächen üben** (zuletzt falsch gelöste Aufgaben)
- **Zeitlimit** bei Wissensaufgaben (abschaltbar)
- **Statistik**: gelöste Aufgaben, Trefferquote, beste Reaktionszeit, letzte 14 Tage, Stärken und Schwächen

## Technik

- `www/index.html` – die ganze App (HTML/CSS/JavaScript)
- `www/tasks.js` – die 500 Aufgaben, erzeugt von `tools/generate_tasks.py`
- Capacitor macht daraus eine Android-App; `.github/workflows/build-apk.yml` baut die APK und veröffentlicht sie als Release.

Aufgaben ändern oder erweitern: `tools/generate_tasks.py` anpassen und hochladen – der Build erzeugt die Aufgaben neu.
