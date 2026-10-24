# Bench – Sitzbank, die zur Trainingsbank wird

Ein Möbelstück für Flur, Bettende oder Wohnzimmer, das gleichzeitig eine vollwertige Flachbank mit Stauraum für Hanteln ist.
Inspiriert von der [Technogym Bench](https://www.technogym.com/en-US/product/technogym-bench_DGY100.html), aber als Holzmöbel zum Selberbauen.

![Bank geschlossen](renders/moebel.png)

| | |
|---|---|
| Maße | 1200 × 400 × 450 mm (L × T × H). Sitzhöhe = Trainingshöhe |
| Material | Birke Multiplex 18 mm, Führungsleiste Buche, Polster mit Kunstleder |
| Stauraum | 2 Fächer × 2 Ebenen hinter 2 Schiebetüren mit Lüftungsschlitzen |
| Inventar | 5 Paar Kurzhanteln 2,5–10 kg, Bänder, Knuckles, Matte (wie Technogym) |
| Belastbar | 120 kg Nutzer, rechnerisch ca. 1,3 mm Durchbiegung an der Vorderkante |
| Gewicht | ca. 38 kg leer, ca. 102 kg mit Hanteln. Rollen zum Ankippen |
| Material­kosten | ca. 400–550 € (Schätzung, ohne Hanteln) |

![Stauraum geöffnet](renders/stauraum.png)

## Dokumente

| Datei | Inhalt |
|---|---|
| [docs/konzept.md](docs/konzept.md) | Idee, „macht das Sinn?“, Zielkonflikte Möbel ↔ Training, Aufbau, Material, Übungen |
| [docs/berechnung.md](docs/berechnung.md) | Stauraum-Belegung, Durchbiegung, Kippsicherheit, Transport *(generiert)* |
| [docs/stueckliste.md](docs/stueckliste.md) | Zuschnitt, Beschläge, Gewicht, Kosten *(generiert)* |
| [cad/bank.scad](cad/bank.scad) | Parametrisches 3D-Modell (OpenSCAD) |
| [params.toml](params.toml) | **Alle Maße an einer Stelle**: hier ändern, nicht im Modell |

## Maße ändern

```bash
# 1. params.toml anpassen (z. B. Länge, Polsterbreite, Hantelmaße)
# 2. alles neu erzeugen: SCAD-Parameter, Stückliste, Berechnung, Renderings
python3 tools/build.py            # braucht Python ≥ 3.11, für Bilder zusätzlich OpenSCAD
python3 tools/build.py --no-render
```

Das Skript prüft dabei, ob das gesamte Inventar in die Fächer passt, und warnt, wenn etwas nicht passt.
Das Modell lässt sich in [OpenSCAD](https://openscad.org) öffnen. Über die Variablen `zeige_tueren`, `zeige_polster`, `zeige_inhalt` und `explosion` schaltet man zwischen den Ansichten um.

## Fahrplan

- [x] **Phase 0 – Konzept:** Machbarkeit, Grundmaße, Stauraum, Statik-Überschlag, 3D-Modell
- [ ] **Phase 1 – Entscheidungen:** Material und Optik, Bezug, Polsterbreite, eigene Hanteln nachmessen
- [ ] **Phase 2 – Detailplanung:** Verbindungsdetails, bemaßte Zeichnungen, DXF für den Zuschnitt
- [ ] **Phase 3 – Probe:** Sitzhöhe auf Kisten testen, Polster-Probestück (Schaumhärte), Musterbrett für die Oberfläche
- [ ] **Phase 4 – Bau**
- [ ] **Phase 5 – Optional:** klappbare Rückenlehne (Schrägbank), Lederbezug, Wandhalterung für weiteres Zubehör
