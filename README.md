# Bench – Sitzbank, die zur Flach- und Schrägbank wird

Ein hochwertiges Möbelstück aus massiver Eiche und Leder für Flur, Bettende oder Wohnzimmer.
Gleichzeitig ist es eine vollwertige Trainingsbank: flach oder mit verstellbarer Rückenlehne von 25° bis 85°, mit Stauraum für Hanteln.
Inspiriert von der [Technogym Bench](https://www.technogym.com/en-US/product/technogym-bench_DGY100.html), die nur flach ist.

![Bank als Möbel](renders/moebel.png)

![Schrägbank 45°](renders/schraeg.png)

| | |
|---|---|
| Maße | 1200 × 400 × 450 mm (L × T × H). Sitzhöhe = Trainingshöhe |
| Stellungen | 0° (flach), 25°, 35°, 45°, 60°, 75°, 85° |
| Material | Eiche massiv 24 mm auf Gehrung, Lamellenfront, Lederpolster, Gelenk schwarz oder Messing |
| Stauraum | 2 Fächer × 2 Ebenen hinter 2 Schiebetüren aus Lamellen |
| Inventar | 5 Paar Kurzhanteln 2,5–10 kg, Bänder, Knuckles, Matte (wie Technogym) |
| Belastbar | 120 kg Nutzer (Überschlagsrechnung mit Stoßfaktor 1,5) |
| Gewicht | ca. 46 kg leer, ca. 110 kg mit Hanteln. Verdeckte Rollen zum Ankippen |
| Materialkosten | ca. 1.000–1.400 € (Schätzung, ohne Hanteln und Polsterei) |

| Verstellbereich | Stauraum |
|---|---|
| ![Verstellung](renders/verstellung.png) | ![Stauraum](renders/stauraum.png) |

## Dokumente

| Datei | Inhalt |
|---|---|
| [docs/konzept.md](docs/konzept.md) | Idee, Schrägbank-Mechanik, Design-Details, Farbvarianten, Zielkonflikte, Aufbau, Material |
| [docs/berechnung.md](docs/berechnung.md) | Rastpositionen und Kräfte, Stauraum-Belegung, Durchbiegung, Kippsicherheit, Transport *(generiert)* |
| [docs/stueckliste.md](docs/stueckliste.md) | Zuschnitt Holz und Stahl, Beschläge, Gewicht, Kosten *(generiert)* |
| [cad/bank.scad](cad/bank.scad) | Parametrisches 3D-Modell (OpenSCAD) |
| [params.toml](params.toml) | **Alle Maße an einer Stelle**: hier ändern, nicht im Modell |

## Maße ändern

```bash
# 1. params.toml anpassen (z. B. Länge, Rastwinkel, Hantelmaße)
# 2. alles neu erzeugen: SCAD-Parameter, Stückliste, Berechnung, Renderings
python3 tools/build.py            # braucht Python ≥ 3.11, für Bilder zusätzlich OpenSCAD
python3 tools/build.py --no-render
```

Das Skript prüft dabei,

- ob die Stütze jeden Rastwinkel erreicht und alle Rasten mit genug Abstand auf die Leisten passen,
- ob das gesamte Inventar in die Fächer passt,
- ob Durchbiegung und Kippsicherheit im Rahmen bleiben.

Es warnt, wenn etwas nicht passt.
Im OpenSCAD-Modell lassen sich `lehne_winkel`, `farbschema` (`"eiche"` oder `"nussbaum"`), `zeige_tueren`, `zeige_inhalt`, `geist` und `explosion` umschalten.

## Fahrplan

- [x] **Phase 0 – Konzept:** Machbarkeit, Grundmaße, Stauraum, Statik-Überschlag, 3D-Modell
- [x] **Phase 0b – Schrägbank und hochwertige Gestaltung:** Klappmechanik mit 7 Stellungen, Massivholz, Leder, Lamellen
- [ ] **Phase 1 – Entscheidungen:** Holzart und Lederfarbe, Gelenk schwarz oder Messing, eigene Hanteln nachmessen
- [ ] **Phase 2 – Detailplanung:** Gelenk- und Stützenzeichnungen für den Laserzuschnitt, Gehrungs- und Nutdetails, bemaßte Zeichnungen
- [ ] **Phase 3 – Probe:** Sitzhöhe und Lehnenwinkel mit einem Pappmodell testen, Schaum-Probestück, Musterbrett für das Öl
- [ ] **Phase 4 – Bau**
- [ ] **Phase 5 – Optionen:** 15°-Zusatzstütze, Sitzkeil, Beinhalter für Crunches
