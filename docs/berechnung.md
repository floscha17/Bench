# Berechnung

> Automatisch erzeugt aus `params.toml` mit `python3 tools/build.py`. Nicht von Hand ändern.
> Überschlagsrechnung zur Plausibilisierung, kein Statik-Nachweis.

## Hauptmaße

- Außen: 1400 × 400 × 450 mm (L × T × H), Sitz- = Trainingshöhe 450 mm
- Polster 370 mm breit, rundum 15 mm eingerückt, 20 mm Schattenfuge darunter
- Sitz 400 mm + Fuge 25 mm + Rückenlehne 945 mm
- Korpus Eiche massiv 24 mm auf Gehrung, Sockel 40 mm zurückgesetzt
- Fächer: 3 × 438,7 mm breit, 332 mm tief
- Schiebetüren: 3 × 477,3 mm, je 22 Lamellen à 17,9 mm

## Schrägbank

Drehachse 25 mm unter der Polsteroberfläche an der Vorderkante der Lehne (x = 440 mm ab linkem Ende). Die Stütze ist 430 mm hinter der Achse angelenkt, 490 mm lang und rastet in zwei Leisten auf dem Deckel ein.

Last: 70 % von 120 kg × 1.5 = 1.236 N auf der Lehne, 350 mm hinter der Achse. Gerechnet sind zwei Lastfälle, das Gewicht senkrecht nach unten und die gleiche Last senkrecht auf die Lehnenfläche (kräftiges Zurücklehnen beim Drücken). Die Tabelle zeigt den ungünstigeren Fall.

| Stellung | Rast ab Achse | Rast ab linkem Ende | Stützkraft | Achskraft | Neigung Stütze |
|---|---:|---:|---:|---:|---:|
| 0° flach (Parkrast, 12 mm tief) | 920 mm | 1.360 mm | – | – | 0° |
| 20° | 889 mm | 1.329 mm | 1.950 N | 1.844 N | 17° |
| 30° | 836 mm | 1.276 mm | 1.308 N | 1.231 N | 26° |
| 45° | 715 mm | 1.155 mm | 1.020 N | 956 N | 40° |
| 60° | 550 mm | 990 mm | 1.044 N | 911 N | 53° |
| 75° | 358 mm | 798 mm | 1.402 N | 1.146 N | 66° |
| 85° | 228 mm | 668 mm | 2.109 N | 2.010 N | 73° |

- Rasttiefe 8 mm, kleinster Abstand zwischen zwei Rasten 31 mm (Minimum 30 mm).
- Knicken der Stütze (2 × Flachstahl 25 × 8): Knicklast 18,4 kN bei max. 2,11 kN → Sicherheit ≈ 8,7.
- Die Achskraft verteilt sich auf zwei Bolzen M10: Scherspannung ≈ 13 N/mm² (zulässig > 100 N/mm²).
- Bei steiler Lehne zieht die Achse nach oben: Die Gelenkplatten werden mit durchgehenden Schrauben und einer Stahl-Gegenplatte unter dem Deckel befestigt, nicht nur mit Holzschrauben.
- Kleinere Winkel als der kleinste Rastwinkel gehen mit einer einzigen Klappstütze nicht: Die Rast läge dann zu nah an der Parkrast.

✅ Alle Rasten liegen auf der Leiste und haben genug Abstand.

## Stauraum-Belegung

Schwerste Teile zuerst, untere Ebene zuerst.

| Zelle | Inhalt | Breite | Höhe | Tiefe | kg |
|---|---|---:|---:|---:|---:|
| Fach 1 unten | Kurzhanteln 10,0 kg (Paar) | 215 | 96 | 286 | 20,0 |
| Fach 1 unten | Kurzhanteln 5,0 kg (Paar) | 175 | 76 | 249 | 10,0 |
| Fach 1 oben | Trainingsmatte (gefaltet) | 340 | 60 | 300 | 1,5 |
| Fach 2 unten | Kurzhanteln 7,5 kg (Paar) | 195 | 86 | 273 | 15,0 |
| Fach 2 unten | Kurzhanteln 3,5 kg (Paar) | 155 | 66 | 236 | 7,0 |
| Fach 2 oben | Widerstandsbänder (3 Stück) | 160 | 60 | 250 | 0,6 |
| Fach 3 unten | Kurzhanteln 2,5 kg (Paar) | 155 | 66 | 202 | 5,0 |
| Fach 3 unten | Gewichtsmanschetten/Knuckles (3 Paar) | 160 | 70 | 220 | 4,9 |

| Zelle | Zugangshöhe | belegt / verfügbar (Breite) |
|---|---:|---:|
| Fach 1 unten | 140 mm | 435 / 439 mm |
| Fach 1 oben | 116 mm | 370 / 439 mm |
| Fach 2 unten | 140 mm | 395 / 439 mm |
| Fach 2 oben | 116 mm | 190 / 439 mm |
| Fach 3 unten | 140 mm | 360 / 439 mm |
| Fach 3 oben | 116 mm | 15 / 439 mm |

✅ Alles Inventar findet Platz.

## Durchbiegung

Lastannahme: 120 kg Nutzer × Stoßfaktor 1.5.

| Bauteil | Last | Stützweite | Durchbiegung | Grenze L/300 | |
|---|---:|---:|---:|---:|---|
| Vorderkante: Deckel + Rastleiste (50 % der Last) | 883 N | 457 mm | 0,77 mm | 1,52 mm | ✅ |
| Lehnenplatte flach zwischen den Rastleisten (Streifen 300 mm) | 1.766 N | 290 mm | 0,55 mm | 0,97 mm | ✅ |
| Rückenlehne schräg, Überstand hinter der Stütze (20°) | 633 N | 515 mm | 1,54 mm | 1,72 mm | ✅ |
| Fachboden Fach 1 (1,5 kg × 2) | 29 N | 439 mm | 0,03 mm | 1,46 mm | ✅ |
| Fachboden Fach 2 (0,6 kg × 2) | 12 N | 439 mm | 0,01 mm | 1,46 mm | ✅ |
| Fachboden Fach 3 (0,0 kg × 2) | 0 N | 439 mm | 0,00 mm | 1,46 mm | ✅ |

Die verleimte Rückwand trägt die Hinterkante des Deckels zusätzlich mit. Sie ist hier nicht angesetzt.

## Kippsicherheit

Der Sockel steht 40 mm hinter der Korpuskante, das Polster 15 mm. Eine Last am Polsterrand liegt also 25 mm außerhalb der Standfläche.

| Fall | leer | mit Inventar |
|---|---:|---:|
| Senkrechte Last auf der Längskante, ab der die Bank kippt | 347 kg | 756 kg |
| Senkrechte Last auf der Stirnkante, ab der die Bank kippt | 1.430 kg | 3.119 kg |
| Lehne 85°: waagerechter Zug/Druck nach hinten an der Lehnenoberkante (1.366 mm hoch), niemand sitzt | 257 N | 560 N |

Sitzt jemand auf dem Sitz, steigt der letzte Wert (leere Bank) auf ≈ 1.243 N. Beim Training ist das unkritisch. Die aufgestellte Lehne ist aber kein Griff zum Hochziehen, wenn die Bank leer ist.

## Transport: vom Bett abrücken

- Zwei Rollen sitzen verdeckt unter dem hinteren Korpusüberstand (Bettseite), 150 mm von den Enden.
- Vorderkante unter dem Überstand fassen und ≈ 48 mm anheben (≈ 8,2° Neigung). Dann rollt die Bank nach vorn, vom Bett weg.
- Dabei zu heben: leer ≈ 25 kg, mit Inventar ≈ 56 kg. Deshalb zuerst die Hanteln herausnehmen, die braucht man fürs Training ohnehin, dann die Bank vorziehen.
- Zum Training die Bank ca. 60 cm vom Bett abrücken: Beim Drücken und bei Fliegenden gehen die Ellbogen unter Polsterhöhe, und beim Sitzen auf der Schrägbank steht ein Fuß neben der Bank.
- Die Rollen sind für glatte Böden (Parkett, Fliesen). Auf Teppich rollen sie schlecht.
