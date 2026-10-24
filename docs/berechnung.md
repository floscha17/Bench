# Berechnung

> Automatisch erzeugt aus `params.toml` mit `python3 tools/build.py`. Nicht von Hand ändern.
> Überschlagsrechnung zur Plausibilisierung, kein Statik-Nachweis.

## Hauptmaße

- Außen: 1200 × 400 × 450 mm (L × T × H), Sitz- = Trainingshöhe 450 mm
- Polster: 65 mm (15 mm Platte + 50 mm Schaum)
- Fächer: 2 × 573,0 mm breit, 332 mm tief, je 2 Ebenen à 145,5 mm
- Schiebetüren: 2 × 602,0 × 296 mm, Durchgriffshöhe 284 mm

## Stauraum-Belegung

Schwerste Teile zuerst, untere Ebene zuerst. Zelle = Fach + Ebene.

| Zelle | Inhalt | Breite | Höhe | Tiefe | kg |
|---|---|---:|---:|---:|---:|
| Fach 1 unten | Kurzhanteln 10 kg (Paar) | 265 | 125 | 310 | 20,0 |
| Fach 1 unten | Kurzhanteln 7,5 kg (Paar) | 241 | 113 | 285 | 15,0 |
| Fach 1 oben | Kurzhanteln 2,5 kg (Paar) | 175 | 80 | 230 | 5,0 |
| Fach 1 oben | Gewichtsmanschetten/Knuckles (3 Paar) | 160 | 70 | 220 | 4,9 |
| Fach 1 oben | Widerstandsbänder (3 Stück) | 160 | 60 | 250 | 0,6 |
| Fach 2 unten | Kurzhanteln 5 kg (Paar) | 215 | 100 | 260 | 10,0 |
| Fach 2 unten | Kurzhanteln 3,5 kg (Paar) | 191 | 88 | 245 | 7,0 |
| Fach 2 oben | Trainingsmatte (gefaltet) | 340 | 60 | 300 | 1,5 |

| Zelle | Zugangshöhe | belegt / verfügbar (Breite) |
|---|---:|---:|
| Fach 1 unten | 146 mm | 551 / 573 mm |
| Fach 1 oben | 120 mm | 555 / 573 mm |
| Fach 2 unten | 146 mm | 451 / 573 mm |
| Fach 2 oben | 120 mm | 370 / 573 mm |

✅ Alles Inventar findet Platz.

## Durchbiegung

Lastannahme: 120 kg Nutzer × Stoßfaktor 1.5.

| Bauteil | Last | Stützweite | Durchbiegung | Grenze L/300 | |
|---|---:|---:|---:|---:|---|
| Vorderkante (Deckel + Buchenleiste, Anteil 50 %) | 883 N | 591 mm | 1,27 mm | 1,97 mm | ✅ |
| Deckel vorne→hinten (Streifen 300 mm, volle Last) | 1.766 N | 332 mm | 0,82 mm | 1,11 mm | ✅ |
| Fachboden Fach 1 (10,5 kg × 2) | 206 N | 573 mm | 0,45 mm | 1,91 mm | ✅ |

Biegespannung Unterkante Buchenleiste: 13,2 N/mm² (Buche massiv ~100 N/mm² Bruch → Sicherheit ≈ 8).
Die Polster-Trägerplatte ist nicht angesetzt und bringt zusätzliche Reserve.

## Kippsicherheit

- Die Seitenwangen stehen bündig mit den Außenkanten auf dem Boden, das Polster steht nicht über.
  **Senkrechte Lasten liegen immer innerhalb der Standfläche → die Bank kann durch Draufsitzen, Aufsteigen oder Abstützen an der Kante nicht kippen.**
- Waagerechte Kraft an der Polsteroberkante, die die Bank leer seitlich kippt: ≈ 167 N (≈ 17 kg)
- Waagerechte Kraft an der Polsteroberkante, die die Bank mit Inventar seitlich kippt: ≈ 447 N (≈ 46 kg)
- Sitzt jemand auf der Bank, steigt dieser Wert um sein Körpergewicht × 0,44 – im Training unkritisch.

## Transport

- Rollen greifen ab ≈ 8,0° Neigung, d. h. linkes Ende am Griffloch um ≈ 167 mm anheben.
- Am Griff anzuheben (halbes Gewicht, mit Inventar): ≈ 51 kg → schwere Hanteln vorher herausnehmen.
