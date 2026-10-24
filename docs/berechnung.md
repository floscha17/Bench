# Berechnung

> Automatisch erzeugt aus `params.toml` mit `python3 tools/build.py`. Nicht von Hand ändern.
> Überschlagsrechnung zur Plausibilisierung, kein Statik-Nachweis.

## Hauptmaße

- Außen: 1400 × 430 × 450 mm (L × T × H), Ecken im Grundriss R 70
- Polster 358 mm breit in einer Wanne mit 20 mm Rand: Rückenlehne 893 mm, Fuge 35 mm, Sitz 400 mm
- Rolltür 1.260 mm lang aus 65 Lamellen à 17,9 mm. Offen läuft sie in die Tasche links (110 mm) und hinter den Fächern entlang (Speicherweg 1.502 mm ✅)
- Fächer: 440, 440, 308 mm breit, 360 mm tief

## Rückenlehne

Drehachse an der inneren Kante, 25 mm unter der Polsteroberfläche (x = 929 mm ab linkem Ende). Das linke Ende hebt sich. Die Stütze ist 390 mm von der Achse angelenkt und 480 mm lang.

Last: 70 % von 120 kg × 1.5 = 1.236 N, 350 mm von der Achse, senkrecht nach unten oder senkrecht auf das Polster. Die Tabelle zeigt den ungünstigeren Fall.

| Stellung | Rast ab Achse | Rast ab linkem Ende | Stützkraft | Achskraft | Neigung Stütze |
|---|---:|---:|---:|---:|---:|
| 0° flach (Parkrast, 12 mm tief) | 870 mm | 59 mm | – | – | 0° |
| 25° | 825 mm | 104 mm | 1.788 N | 1.627 N | 20° |
| 35° | 770 mm | 159 mm | 1.323 N | 1.173 N | 28° |
| 45° | 696 mm | 233 mm | 1.143 N | 993 N | 37° |
| 60° | 557 mm | 372 mm | 1.122 N | 929 N | 48° |
| 75° | 399 mm | 530 mm | 1.365 N | 1.024 N | 58° |
| 85° | 298 mm | 631 mm | 1.759 N | 1.531 N | 63° |

- Kleinster Abstand zwischen zwei Rasten 45 mm (Minimum 30 mm).
- Knicken der Stütze (2 × Flachstahl 25 × 8): Knicklast 19,2 kN bei max. 1,79 kN → Sicherheit ≈ 10,7.
- Achskraft auf zwei Bolzen M10: Scherspannung ≈ 10 N/mm² (zulässig > 100 N/mm²).

✅ Alle Rasten liegen auf der Leiste und haben genug Abstand.

Bei steilen Stellungen zieht die Achse nach oben. Die Gelenkplatten werden deshalb mit durchgehenden Schrauben auf eine Stahl-Gegenplatte unter dem Deckel geschraubt.

## Sitz

Drehachse an der inneren Kante (x = 964 mm ab linkem Ende), 25 mm unter der Polsteroberfläche. Das rechte Ende hebt sich, damit man auf der Schrägbank nicht nach vorn rutscht. Getragen wird der Sitz von Klappbügeln aus Stahl, einer je Stellung, ineinander geschachtelt. Der benutzte Bügel wird hochgeklappt und steht senkrecht, die anderen liegen flach in der Wanne.

Last: 100 % von 120 kg × 1.5 = 1.766 N, 150 mm von der Achse, senkrecht auf das Polster.

| Stellung | Bügel ab Achse | Bügelhöhe über Deckel | Kraft auf den Bügel | Achskraft |
|---|---:|---:|---:|---:|
| 0° flach | – | alle Bügel liegen flach | – | – |
| 10° | 340 mm | 79 mm | 779 N | 987 N |
| 20° | 315 mm | 132 mm | 841 N | 925 N |

✅ Die Bügel passen umgeklappt unter den Sitz.

## Stauraum-Belegung

Schwerste Teile zuerst, untere Ebene zuerst. Die Hanteln liegen auf einer schwarzen Ablage.

| Zelle | Inhalt | Breite | Höhe | Tiefe | kg |
|---|---|---:|---:|---:|---:|
| Fach 1 unten | Kurzhanteln 10,0 kg (Paar) | 215 | 106 | 286 | 20,0 |
| Fach 1 unten | Kurzhanteln 5,0 kg (Paar) | 175 | 86 | 249 | 10,0 |
| Fach 1 oben | Gewichtsmanschetten/Knuckles (3 Paar) | 160 | 70 | 220 | 4,9 |
| Fach 1 oben | Widerstandsbänder (3 Stück) | 160 | 60 | 250 | 0,6 |
| Fach 2 unten | Kurzhanteln 7,5 kg (Paar) | 195 | 96 | 273 | 15,0 |
| Fach 2 unten | Kurzhanteln 3,5 kg (Paar) | 155 | 76 | 236 | 7,0 |
| Fach 2 oben | Trainingsmatte (gefaltet) | 340 | 60 | 300 | 1,5 |
| Fach 3 unten | Kurzhanteln 2,5 kg (Paar) | 155 | 76 | 202 | 5,0 |

| Zelle | lichte Höhe | belegt / verfügbar (Breite) | davon vorn offen |
|---|---:|---:|---:|
| Fach 1 unten | 130 mm | 435 / 440 mm | 440 mm |
| Fach 1 oben | 121 mm | 365 / 440 mm | 440 mm |
| Fach 2 unten | 130 mm | 395 / 440 mm | 440 mm |
| Fach 2 oben | 121 mm | 370 / 440 mm | 440 mm |
| Fach 3 unten | 130 mm | 185 / 308 mm | 262 mm |
| Fach 3 oben | 121 mm | 15 / 308 mm | 262 mm |

✅ Alles Inventar findet Platz.

## Durchbiegung

Lastannahme: 120 kg Nutzer × Stoßfaktor 1.5.

| Bauteil | Last | Stützweite | Durchbiegung | Grenze L/300 | |
|---|---:|---:|---:|---:|---|
| Vorderkante: Frontleiste mit Rand + Deckel + Rastleiste (50 % der Last) | 883 N | 458 mm | 0,42 mm | 1,53 mm | ✅ |
| Lehnenplatte flach zwischen den Rastleisten (Streifen 300 mm) | 1.766 N | 278 mm | 0,48 mm | 0,93 mm | ✅ |
| Rückenlehne schräg, Überstand hinter der Stütze (25°) | 631 N | 503 mm | 1,45 mm | 1,68 mm | ✅ |
| Sitz schräg, Überstand hinter der Stütze (10°) | 261 N | 60 mm | 0,01 mm | 0,20 mm | ✅ |
| Fachboden Fach 1 (5,5 kg × 2) | 108 N | 440 mm | 0,10 mm | 1,47 mm | ✅ |
| Fachboden Fach 2 (1,5 kg × 2) | 29 N | 440 mm | 0,03 mm | 1,47 mm | ✅ |
| Fachboden Fach 3 (0,0 kg × 2) | 0 N | 308 mm | 0,00 mm | 1,03 mm | ✅ |

Die verleimte Rückwand trägt die Hinterkante des Deckels zusätzlich mit. Sie ist hier nicht angesetzt.

## Kippsicherheit

Die Bank steht auf 4 Füßen, deren Außenkante 40 mm hinter der Korpuskante liegt. Das Polster beginnt 36 mm hinter der Kante.

| Fall | leer | mit Inventar |
|---|---:|---:|
| Senkrechte Last auf der Längskante, ab der die Bank kippt | > 1.000 kg (kippt praktisch nicht) | > 1.000 kg (kippt praktisch nicht) |
| Senkrechte Last auf der Stirnkante, ab der die Bank kippt | > 1.000 kg (kippt praktisch nicht) | > 1.000 kg (kippt praktisch nicht) |
| Lehne 85°: waagerechter Druck nach hinten an der Lehnenoberkante (1.315 mm hoch), niemand sitzt | 320 N | 635 N |

Sitzt jemand auf dem Sitz, steigt der letzte Wert (leere Bank) auf ≈ 1.326 N. Beim Training ist das unkritisch. Die aufgestellte Lehne ist aber kein Griff zum Hochziehen, wenn die Bank leer ist.

## Absenkrollen: vom Bett abrücken

- 4 lenkbare Doppelrollen Ø 40 mm sitzen verdeckt im Sockel. Eine Exzenterwelle hebt sie gemeinsam.
- Bronze-Fußhebel vorn rechts nach unten treten: Die Rollen fahren 6 mm unter die Füße, und die Bank rollt in jede Richtung.
  Hebel mit der Fußspitze hochziehen: Die Bank steht wieder fest auf den Füßen. Der Hebel rastet in beiden Lagen über den Totpunkt.
- Fußkraft am Hebel (≈ 50 mm Weg, mit Reibung): leer ≈ 10 kg, mit Inventar ≈ 20 kg.
- Zum Training die Bank ca. 60 cm vom Bett wegrollen: Beim Drücken und bei Fliegenden gehen die Ellbogen unter Polsterhöhe, und auf der Schrägbank steht ein Fuß neben der Bank. Vor dem Training die Rollen hochstellen.
- Die Rollen sind für glatte Böden (Parkett, Fliesen) gedacht.
