# Bench – Bank am Bettende, die zur Flach- und Schrägbank wird

Ein hochwertiges Möbelstück aus massiver Eiche und Cognac-Leder für das Ende eines 180-cm-Betts.
Gleichzeitig ist es eine vollwertige Trainingsbank: flach oder mit verstellbarer Rückenlehne von 20° bis 85°.
Im Stauraum liegen passgenau selbstgebaute Hanteln. Gebaut wird die Bank von einem Schreiner.

![Bank als Möbel](renders/moebel.png)

![Schrägbank 45°](renders/schraeg.png)

| | |
|---|---|
| Maße | 1400 × 400 × 450 mm (L × T × H). Sitzhöhe = Trainingshöhe |
| Stellungen | 0° (flach), 20°, 30°, 45°, 60°, 75°, 85° |
| Material | Eiche massiv 24 mm auf Gehrung, Lamellen-Schiebetüren, Cognac-Leder, Gelenk schwarz |
| Stauraum | 3 Fächer × 2 Ebenen hinter 3 Schiebetüren |
| Hanteln | 5 Paar, 2,5–10 kg, Stahlköpfe schwarz mit Eichengriff, selbstgebaut ([hanteln.md](docs/hanteln.md)) |
| Belastbar | 120 kg Nutzer (Überschlagsrechnung mit Stoßfaktor 1,5) |
| Gewicht | ca. 54 kg leer, ca. 118 kg mit Hanteln. Verdeckte Rollen zum Abrücken vom Bett |
| Kosten | grob 3.900–7.200 € mit Schreiner, Polsterei und Metallbau, plus Hanteln ca. 450–750 € |

| Verstellbereich | Stauraum |
|---|---|
| ![Verstellung](renders/verstellung.png) | ![Stauraum](renders/stauraum.png) |

## Dokumente

| Datei | Inhalt |
|---|---|
| [docs/schreiner.md](docs/schreiner.md) · [PDF](docs/schreiner-mappe.pdf) | **Unterlagen für den Schreiner**: Vorgaben, Zeichnungen, kritische Maße, Ablauf, Anfrage-Text |
| [docs/konzept.md](docs/konzept.md) | Idee, Bettende, Leder, Schrägbank-Mechanik, Design, Zielkonflikte, Aufbau |
| [docs/hanteln.md](docs/hanteln.md) | Selbstbau-Hanteln: Maße je Gewicht, Fertigung, Kosten *(generiert)* |
| [docs/berechnung.md](docs/berechnung.md) | Rasten und Kräfte, Stauraum-Belegung, Durchbiegung, Kippsicherheit, Transport *(generiert)* |
| [docs/stueckliste.md](docs/stueckliste.md) | Zuschnitt Holz und Stahl, Beschläge, Gewicht, Kosten *(generiert)* |
| [docs/zeichnungen/](docs/zeichnungen) | Maßskizzen: Übersicht, Querschnitt, Rastleiste, Metallteile, Hantel *(generiert)* |
| [cad/bank.scad](cad/bank.scad) | Parametrisches 3D-Modell (OpenSCAD) |
| [params.toml](params.toml) | **Alle Maße an einer Stelle**: hier ändern, nicht im Modell |

## Maße ändern

```bash
# 1. params.toml anpassen (z. B. Länge, Rastwinkel, Hantelgewichte)
# 2. alles neu erzeugen: SCAD-Parameter, Stückliste, Berechnung, Hanteln, Zeichnungen, Renderings
python3 tools/build.py            # Python ≥ 3.11, für Bilder zusätzlich OpenSCAD
python3 tools/build.py --no-render
python3 tools/build.py --stuetze-suchen   # passende Stütze finden, wenn Lehne oder Winkel geändert wurden
python3 tools/mappe.py            # PDF für den Schreiner (braucht Python-Paket markdown + Node/Playwright)
```

Das Skript prüft dabei,

- ob die Stütze jeden Rastwinkel erreicht und alle Rasten mit genug Abstand auf die Leisten passen,
- ob Hanteln und Zubehör in die Fächer passen,
- ob Durchbiegung und Kippsicherheit im Rahmen bleiben.

Es warnt, wenn etwas nicht passt.

## Fahrplan

- [x] **Konzept:** Machbarkeit, Maße, Stauraum, Statik-Überschlag, 3D-Modell
- [x] **Schrägbank und Design:** Klappmechanik mit 7 Stellungen, Eiche massiv, Leder, Lamellen
- [x] **Festlegungen:** 180-cm-Bett → 140 cm Länge, Eiche + Cognac, Hanteln Stahl/Eiche
- [x] **Unterlagen:** Schreiner-Mappe, Zeichnungen, Hantelmaße
- [ ] **Angebote:** Schreiner (mit Metallbau und Polsterei), Dreherei für die Hantelköpfe
- [ ] **Probe:** Höhe und Lehnenwinkel testen, Musterbrett Öl, Lederprobe
- [ ] **Bau**
- [ ] **Optionen:** Sitzkeil, Beinhalter für Crunches
