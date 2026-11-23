# KognitivTrainer

Android-App mit **1000 Aufgaben** zum Trainieren von Kopf und Reaktion – komplett offline, alle Ergebnisse bleiben auf dem Handy.

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
| 🌍 Allgemeinwissen | 500 | Geografie, Geschichte, Naturwissenschaft, Biologie & Mensch, Astronomie, Kunst & Literatur, Musik, Sport, Sprache, Technik, Gesellschaft, Essen & Alltag, Flaggen, Landkarten |

Jede Aufgabe hat eine Stufe (leicht / mittel / schwer) und eine Erklärung, die nach dem Lösen angezeigt wird.

## Funktionen

- **Tägliches Training**: jeden Tag 10 Aufgaben aus allen Bereichen, mit Serie (🔥)
- **Pro Bereich zwei Zufallsknöpfe**: „Zufall endlos“ (alle Aufgaben, gemischte Arten und Stufen, nie dieselbe direkt hintereinander) und „Offene zufällig“ (noch nie gemachte und zuletzt falsch gelöste Aufgaben, bis alle zuletzt richtig sind)
- **Zufallsmix** und **Schwächen üben** (zuletzt falsch gelöste Aufgaben)
- **Zeitlimit** bei Wissensaufgaben (abschaltbar)
- **Statistik**: gelöste Aufgaben, Trefferquote, beste Reaktionszeit, letzte 14 Tage, Stärken und Schwächen

## Technik

- `www/index.html` – die ganze App (HTML/CSS/JavaScript)
- `www/tasks.js` – alle Aufgaben, erzeugt von `tools/generate_tasks.py`
- `tools/wissen/*.txt` – die Allgemeinwissensfragen (eine Zeile pro Frage: Stufe|Thema|Frage|richtig|falsch|falsch|falsch|Erklärung)
- `www/flags/`, `www/worldmap.js` – Flaggen (flag-icons, MIT) und Weltkarte (@svg-maps/world, CC BY 4.0)
- Capacitor macht daraus eine Android-App; `.github/workflows/build-apk.yml` baut die APK und veröffentlicht sie als Release.

Aufgaben ändern oder erweitern: `tools/generate_tasks.py` anpassen und hochladen – der Build erzeugt die Aufgaben neu.
