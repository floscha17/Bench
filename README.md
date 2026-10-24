# Bench – Wohnbank am Bettende, die zur Flach- und Schrägbank wird

Ein hochwertiges Möbel aus Eiche und Cognac-Leder für das Ende eines 180-cm-Betts, nach dem [Studio-Vorentwurf V01](docs/vorentwurf-studio.pdf) und dem [Bildentwurf](docs/bildentwurf.png).
Gleichzeitig ist es eine vollwertige Trainingsbank: Rückenlehne 15°–60°, Sitz 10° oder 15°, formschlüssig verriegelt auf einem innenliegenden Stahlrahmen.
Hinter einer Rollfront aus Eichenlamellen hängen die selbstgebauten Hanteln in Einzelaufnahmen. Gebaut wird die Bank vom Schreiner mit Polsterei und Metallbau.

| Möbel | Training |
|---|---|
| ![Bank als Möbel](renders/moebel.png) | ![Training](renders/training.png) |

| | |
|---|---|
| Maße | 1200 × 430 × 450 mm (L × T × H), Ecken R 70. Sitzhöhe = Trainingshöhe |
| Stellungen | Lehne 0°, 15°, 30°, 45°, 60°. Sitz 0°, 10°, 15°. Gemeinsame Drehachse, Gleitstützen mit Indexbolzen |
| Tragwerk | Stahlrahmen trägt Polster, Hanteln und Füße. Die Holzverkleidung trägt nicht mit |
| Material | Eiche furniert mit formverleimten Rundungen, Lamellen Eiche massiv, Cognac-Leder mit Eichenkante, Stahl schwarz, Bronze-Pedal |
| Stauraum | Tasche für die Rollfront, Hantelbereich auf 2 Ebenen, Zubehörfach mit Fachboden |
| Hanteln | 5 Paar, 2,5–10 kg, Stahlköpfe schwarz mit Eichengriff, selbstgebaut ([hanteln.md](docs/hanteln.md)) |
| Belastbar | 120 kg Nutzer (Überschlagsrechnung mit Stoßfaktor 1,5, Nachweis durch den Metallbau) |
| Gewicht | ca. 71 kg leer, ca. 135 kg mit Hanteln. Verdecktes Fahrwerk mit Fußpedal zum Abrücken vom Bett |
| Kosten | grob 6.600–12.200 € in vier Gewerken, plus Hanteln ca. 460–730 € |

| Tragwerk | Verstellbereich |
|---|---|
| ![Tragwerk](renders/tragwerk.png) | ![Verstellung](renders/verstellung.png) |

## Dokumente

| Datei | Inhalt |
|---|---|
| [docs/schreiner.md](docs/schreiner.md) · [PDF](docs/schreiner-mappe.pdf) | **Unterlagen für den Schreiner**: Abweichungen vom Vorentwurf, Gewerke, kritische Maße, Zeichnungen, Vorgaben, offene Punkte, Anfrage-Text |
| [docs/vorentwurf-studio.pdf](docs/vorentwurf-studio.pdf) | Studio-Vorentwurf V01: Gestaltung, Maße, Funktionsskizzen, Briefing |
| [docs/konzept.md](docs/konzept.md) | Entwicklung, Abgleich mit dem Vorentwurf, Bettende, Leder, Mechanik, Design, Aufbau, Kosten |
| [docs/hanteln.md](docs/hanteln.md) | Selbstbau-Hanteln: Maße je Gewicht, Fertigung, Kosten *(generiert)* |
| [docs/berechnung.md](docs/berechnung.md) | Rastpositionen und Kräfte, Fuge, Stauraum-Belegung, Durchbiegung, Kippsicherheit, Fahrwerk *(generiert)* |
| [docs/stueckliste.md](docs/stueckliste.md) | Planungsstand nach Gewerken, Gewicht, Kosten *(generiert)* |
| [docs/zeichnungen/](docs/zeichnungen) | Maßskizzen: Übersicht, Querschnitt, Gleitschienen, Metallteile, Hantel *(generiert)* |
| [cad/bank.scad](cad/bank.scad) | Parametrisches 3D-Modell (OpenSCAD) |
| [params.toml](params.toml) | **Alle Maße an einer Stelle**: hier ändern, nicht im Modell |

## Maße ändern

```bash
# 1. params.toml anpassen (z. B. Länge, Rastwinkel, Hantelgewichte)
# 2. alles neu erzeugen: SCAD-Parameter, Stückliste, Berechnung, Hanteln, Zeichnungen, Renderings
python3 tools/build.py            # Python ≥ 3.11, für Bilder zusätzlich OpenSCAD
python3 tools/build.py --no-render
python3 tools/build.py --stuetze-suchen   # passende Gleitstütze finden, wenn Polster oder Winkel geändert wurden
python3 tools/mappe.py            # PDF für den Schreiner (braucht Python-Paket markdown + Node/Playwright)
```

Das Skript prüft dabei,

- ob jede Gleitstütze alle Winkel erreicht und die Rastlöcher mit genug Abstand auf die Schienen passen,
- ob die Polsterkanten in jeder Stellungskombination Abstand halten,
- ob Hanteln und Zubehör neben den Rahmenstützen in die Fächer passen,
- ob Durchbiegung und Kippsicherheit im Rahmen bleiben.

Es warnt, wenn etwas nicht passt.

## Fahrplan

- [x] **Konzept:** Machbarkeit, Maße, Stauraum, Statik-Überschlag, 3D-Modell
- [x] **Schrägbank und Design:** Klappmechanik, Eiche, Leder, Lamellen
- [x] **Festlegungen:** 180-cm-Bett, Eiche + Cognac, Hanteln Stahl/Eiche
- [x] **Design nach Bildentwurf:** Rundungen, Rollfront, Polsterwanne, neigbarer Sitz, Fahrwerk
- [x] **Studio-Vorentwurf eingearbeitet:** 1200 mm, Stahlrahmen, verriegelnde Gleitstützen, Hanteln einzeln gesichert, Angebot nach Gewerken
- [ ] **Angebote:** Holzbau, Polster, Metallbau/Beschläge, Fahrwerk; Dreherei für die Hantelköpfe
- [ ] **Probe:** Liegeprobe, Pappmodell der Hantelaufnahmen, Musterbrett Öl, Lederprobe, Rolladensystem
- [ ] **Bau**
- [ ] **Optionen:** Spindelantrieb statt Pedal, Beinhalter für Crunches, Nussbaum-Variante
