# Berechnung

> Automatisch erzeugt aus `params.toml` mit `python3 tools/build.py`. Nicht von Hand ändern.
> Überschlagsrechnung zur Abstimmung. Den Nachweis von Lasten, Verbindungen, Verriegelung und Kippsicherheit übernehmen Metallbau bzw. Beschlaglieferant.

## Hauptmaße

- Außen: 1200 × 430 × 450 mm (L × T × H), Ecken im Grundriss R 70
- Längskette: 22 + Lehne 810 + Fuge 16 + Sitz 330 + 22 = 1200 mm
- Polsterbreite 368 mm (Rand 19 + Spalt 12 je Seite für die Gelenkkonsolen)
- Höhe: Sockel 70 + Korpus 310 + Polsterpaket 70 = 450 mm
- Rolltür 1.060 mm aus 54 Lamellen à 18,2 mm, Speicherweg links und hinten 1.331 mm ✅
- Innenraum: Tasche 100 mm, Hantelbereich 660 mm, Zubehör 378 mm, 369 mm tief, 247 mm hoch

## Rückenlehne

Gemeinsame Drehachse mit dem anderen Polster in der Mitte der Fuge, 12 mm unter der Polsteroberfläche (x = 840 mm ab linkem Ende). Das linke Ende hebt sich. Die Gleitstütze ist 390 mm von der Achse angelenkt und 390 mm lang. Ihr Fuß gleitet in einer C-Schiene und wird in jeder Arbeitsstellung von einem federnden Indexbolzen Ø 10 formschlüssig verriegelt. Flach liegt das Polster auf dem Rahmen, der Gleitschuh steht am Endanschlag und wird von einem Kugelschnäpper gegen Abheben gehalten.

Last: 70 % von 120 kg × 1.5 = 1.236 N, 350 mm von der Achse, senkrecht nach unten oder senkrecht auf das Polster. Die Tabelle zeigt den ungünstigeren Fall.

| Stellung | Loch / Anschlag ab Achse | ab linkem Ende | Stützkraft | Achskraft | Neigung Stütze |
|---|---:|---:|---:|---:|---:|
| 0° | 780 mm | 60 mm | – | – | 2° |
| 15° | 766 mm | 74 mm | 2.801 N | 2.596 N | 17° |
| 30° | 694 mm | 146 mm | 1.346 N | 1.125 N | 34° |
| 45° | 561 mm | 279 mm | 1.096 N | 793 N | 52° |
| 60° | 325 mm | 515 mm | 1.421 N | 1.113 N | 79° |

- Kleinster Lochabstand 71 mm (Minimum 22 mm). Ein eigenes Loch für flach ginge nicht: Es läge nur gut 10 mm neben dem Loch für den kleinsten Winkel.
- Knicken der Stütze (2 × Flachstahl 25 × 8): Knicklast 29,1 kN bei max. 2,80 kN → Sicherheit ≈ 10,4.
- Indexbolzen Ø 10, je Bein zweischnittig: Scherspannung ≈ 9 N/mm² (Stahl zulässig > 100 N/mm²).

✅ Alle Löcher liegen auf der Schiene und haben genug Abstand.

## Sitz

Gemeinsame Drehachse mit dem anderen Polster in der Mitte der Fuge, 12 mm unter der Polsteroberfläche (x = 840 mm ab linkem Ende). Das rechte Ende hebt sich. Die Gleitstütze ist 230 mm von der Achse angelenkt und 80 mm lang. Ihr Fuß gleitet in einer C-Schiene und wird in jeder Arbeitsstellung von einem federnden Indexbolzen Ø 10 formschlüssig verriegelt. Flach liegt das Polster auf dem Rahmen, der Gleitschuh steht am Endanschlag und wird von einem Kugelschnäpper gegen Abheben gehalten.

Last: 100 % von 120 kg × 1.5 = 1.766 N, 150 mm von der Achse, senkrecht nach unten oder senkrecht auf das Polster. Die Tabelle zeigt den ungünstigeren Fall.

| Stellung | Loch / Anschlag ab Achse | ab linkem Ende | Stützkraft | Achskraft | Neigung Stütze |
|---|---:|---:|---:|---:|---:|
| 0° | 309 mm | 1.149 mm | – | – | 9° |
| 10° | 297 mm | 1.137 mm | 1.851 N | 1.439 N | 42° |
| 15° | 267 mm | 1.107 mm | 1.192 N | 819 N | 69° |

- Kleinster Lochabstand 29 mm (Minimum 22 mm). Ein eigenes Loch für flach ginge nicht: Es läge nur gut 10 mm neben dem Loch für den kleinsten Winkel.
- Knicken der Stütze (2 × Flachstahl 25 × 8): Knicklast 690,9 kN bei max. 1,85 kN → Sicherheit ≈ 373,2.
- Indexbolzen Ø 10, je Bein zweischnittig: Scherspannung ≈ 6 N/mm² (Stahl zulässig > 100 N/mm²).

✅ Alle Löcher liegen auf der Schiene und haben genug Abstand.

## Fuge zwischen Lehne und Sitz

Lehne und Sitz drehen um eine gemeinsame Achse in der Fugenmitte, 12 mm unter der Oberfläche. Die Polsterkanten sind mit R 12 gerundet und wandern beim Anstellen nur wenig in die Fuge. Kleinster Abstand über alle Stellungen: **5,3 mm** (Lehne 60°, Sitz 15°, Fuge 16 mm). ✅

Mit einer Achse unten am Polster, wie in der Funktionsskizze des Vorentwurfs angedeutet, würden die oberen Kanten bei 60° rund 61 mm in die Fuge wandern. Deshalb sitzt die Achse oben, getragen von schmalen Konsolen im Spalt neben den Polstern. Zwei getrennte Achsen gingen bei so kleiner Fuge nicht: Zwei Bolzen M10 brauchen mehr als 16 mm Abstand.

## Stauraum

Hanteln einzeln in Aufnahmen auf Stahltraversen zwischen den Rahmenstützen, schwerste unten. Zubehör im Zubehörbereich; was in der Tiefe an die Stützen reicht, liegt daneben (die Matte quer).

| Bereich | Inhalt | Breite | Höhe | Tiefe | kg |
|---|---|---:|---:|---:|---:|
| Hantelbereich unten | Kurzhantel 10,0 kg (1) | 110 | 112 | 286 | 10,0 |
| Hantelbereich unten | Kurzhantel 10,0 kg (2) | 110 | 112 | 286 | 10,0 |
| Hantelbereich unten | Kurzhantel 7,5 kg (1) | 100 | 102 | 273 | 7,5 |
| Hantelbereich unten | Kurzhantel 7,5 kg (2) | 100 | 102 | 273 | 7,5 |
| Hantelbereich unten | Kurzhantel 5,0 kg (1) | 90 | 92 | 249 | 5,0 |
| Hantelbereich oben | Kurzhantel 5,0 kg (2) | 90 | 92 | 249 | 5,0 |
| Hantelbereich oben | Kurzhantel 3,5 kg (1) | 80 | 82 | 236 | 3,5 |
| Hantelbereich oben | Kurzhantel 3,5 kg (2) | 80 | 82 | 236 | 3,5 |
| Hantelbereich oben | Kurzhantel 2,5 kg (1) | 80 | 82 | 202 | 2,5 |
| Hantelbereich oben | Kurzhantel 2,5 kg (2) | 80 | 82 | 202 | 2,5 |
| Zubehör unten | Gewichtsmanschetten/Knuckles (3 Paar) | 160 | 70 | 220 | 4,9 |
| Zubehör unten | Widerstandsbänder (3 Stück) | 160 | 60 | 250 | 0,6 |
| Zubehör oben | Trainingsmatte (gefaltet) | 300 | 60 | 340 | 1,5 |

| Bereich | lichte Höhe | belegt / verfügbar (Breite) | davon vorn offen |
|---|---:|---:|---:|
| Hantelbereich unten | 128 mm | 602 / 660 mm | 660 mm |
| Hantelbereich oben | 107 mm | 502 / 660 mm | 660 mm |
| Zubehör unten | 128 mm | 350 / 378 mm | 327 mm |
| Zubehör oben | 107 mm | 320 / 378 mm | 327 mm |

✅ Alle 10 Hanteln und das Zubehör finden Platz.

Die Breiten gelten für die selbstgebauten Hanteln aus [hanteln.md](hanteln.md). Vor der Fertigung werden die fertigen Hanteln vermessen und die Aufnahmen danach gesetzt.

## Durchbiegung

Lastannahme: 120 kg Nutzer × Stoßfaktor 1.5. Die Lasten laufen über den Innenrahmen direkt in die Füße, die Holzverkleidung trägt nicht mit.

| Bauteil | Last | Stützweite | Durchbiegung | Grenze L/300 | |
|---|---:|---:|---:|---:|---|
| Längsrohr 50 × 25 × 3 (50 % der Last) | 883 N | 626 mm | 0,54 mm | 2,09 mm | ✅ |
| Polsterplatte zwischen den Längsrohren (Streifen 300 mm) | 1.766 N | 286 mm | 0,53 mm | 0,95 mm | ✅ |
| Rückenlehne angestellt, Überstand hinter der Stütze | 631 N | 428 mm | 0,89 mm | 1,43 mm | ✅ |
| Sitz angestellt, Überstand hinter der Stütze | 569 N | 108 mm | 0,07 mm | 0,36 mm | ✅ |
| Hantel-Traverse obere Ebene (17,0 kg × 2, je Traverse) | 167 N | 660 mm | 0,17 mm | 2,20 mm | ✅ |

## Kippsicherheit

Die Füße sitzen unter den Eckstützen des Innenrahmens. Standfläche x = 128…1.183 mm, y = 42…388 mm.

| Fall | leer | mit Hanteln |
|---|---:|---:|
| Senkrechte Last an der Längskante | liegt innerhalb der Standfläche | kippt nicht |
| Senkrechte Last am linken Lehnenende, ab der die Bank kippt | 314 kg | 599 kg |
| Senkrechte Last am rechten Sitzende | liegt innerhalb der Standfläche | kippt nicht |
| Lehne 60°: waagerechter Druck nach hinten an der Lehnenoberkante (1.139 mm hoch), niemand sitzt | 287 N | 547 N |

Zum Vergleich: 120 kg × 1.5 = 180 kg. Step-ups oder Aufstützen genau am Lehnenende sind damit abgedeckt; die Lehne ist aber kein Griff zum Hochziehen.

## Fahrwerk

- Trainieren: Die Bank steht auf 4 Stellfüßen an den Eckstützen. Die 4 Lenkrollen Ø 50 haben Bodenfreiheit.
- Rollen: Bronze-Pedal rechts im Sockel treten. Zwei gekoppelte Exzenterwellen senken den geführten Rollenrahmen ab und heben die Füße 8 mm an.
- Pedalkraft (≈ 50 mm Weg, mit Reibung): leer ≈ 15 kg, mit Hanteln ≈ 28 kg.
- Transportstellung über Totpunkt verriegelt. Beim Verschieben: Polster flach, Rolltür zu, niemand auf der Bank.
- Option: elektrischer Taster mit Spindelantrieb statt Pedal.
