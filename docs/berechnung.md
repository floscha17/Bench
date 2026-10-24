# Berechnung

> Automatisch erzeugt aus `params.toml` mit `python3 tools/build.py`. Nicht von Hand ändern.
> Überschlagsrechnung zur Plausibilisierung, kein Statik-Nachweis.

## Hauptmaße

- Außen: 1200 × 400 × 450 mm (L × T × H), Sitz- = Trainingshöhe 450 mm
- Polster 370 mm breit, rundum 15 mm eingerückt, 20 mm Schattenfuge darunter
- Sitz 340 mm + Fuge 25 mm + Rückenlehne 805 mm
- Korpus Eiche massiv 24 mm auf Gehrung, Sockel 40 mm zurückgesetzt
- Fächer: 2 × 567,0 mm breit, 332 mm tief
- Schiebetüren: 2 × 596,0 mm, je 27 Lamellen à 18,2 mm

## Schrägbank

Drehachse 25 mm unter der Polsteroberfläche an der Vorderkante der Lehne (x = 380 mm ab linkem Ende). Die Stütze ist 370 mm hinter der Achse angelenkt, 410 mm lang und rastet in zwei Leisten auf dem Deckel ein.

Last: 70 % von 120 kg × 1.5 = 1.236 N auf der Lehne, 350 mm hinter der Achse. Gerechnet sind zwei Lastfälle, das Gewicht senkrecht nach unten und die gleiche Last senkrecht auf die Lehnenfläche (kräftiges Zurücklehnen beim Drücken). Die Tabelle zeigt den ungünstigeren Fall.

| Stellung | Rast ab Achse | Rast ab linkem Ende | Stützkraft | Achskraft | Neigung Stütze |
|---|---:|---:|---:|---:|---:|
| 0° flach (Parkrast, 12 mm tief) | 780 mm | 1.160 mm | – | – | 0° |
| 25° | 735 mm | 1.115 mm | 1.805 N | 1.591 N | 23° |
| 35° | 679 mm | 1.059 mm | 1.346 N | 1.120 N | 32° |
| 45° | 603 mm | 983 mm | 1.181 N | 926 N | 42° |
| 60° | 455 mm | 835 mm | 1.224 N | 844 N | 56° |
| 75° | 270 mm | 650 mm | 1.780 N | 1.514 N | 72° |
| 85° | 105 mm | 485 mm | 4.246 N | 4.248 N | 87° |

- Rasttiefe 8 mm, kleinster Abstand zwischen zwei Rasten 45 mm (Minimum 30 mm).
- Knicken der Stütze (2 × Flachstahl 25 × 8): Knicklast 26,3 kN bei max. 4,25 kN → Sicherheit ≈ 6,2.
- Die Achskraft verteilt sich auf zwei Bolzen M10: Scherspannung ≈ 27 N/mm² (zulässig > 100 N/mm²).
- Bei steiler Lehne zieht die Achse nach oben: Die Gelenkplatten werden mit durchgehenden Schrauben und einer Stahl-Gegenplatte unter dem Deckel befestigt, nicht nur mit Holzschrauben.
- Kleinere Winkel als der kleinste Rastwinkel gehen mit einer einzigen Klappstütze nicht: Die Rast läge dann zu nah an der Parkrast.

✅ Alle Rasten liegen auf der Leiste und haben genug Abstand.

## Stauraum-Belegung

Schwerste Teile zuerst, untere Ebene zuerst.

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
| Fach 1 unten | 140 mm | 551 / 567 mm |
| Fach 1 oben | 116 mm | 555 / 567 mm |
| Fach 2 unten | 140 mm | 451 / 567 mm |
| Fach 2 oben | 116 mm | 370 / 567 mm |

✅ Alles Inventar findet Platz.

## Durchbiegung

Lastannahme: 120 kg Nutzer × Stoßfaktor 1.5.

| Bauteil | Last | Stützweite | Durchbiegung | Grenze L/300 | |
|---|---:|---:|---:|---:|---|
| Vorderkante: Deckel + Rastleiste (50 % der Last) | 883 N | 585 mm | 1,62 mm | 1,95 mm | ✅ |
| Lehnenplatte flach zwischen den Rastleisten (Streifen 300 mm) | 1.766 N | 290 mm | 0,55 mm | 0,97 mm | ✅ |
| Rückenlehne schräg, Überstand hinter der Stütze (25°) | 605 N | 435 mm | 1,34 mm | 1,45 mm | ✅ |
| Fachboden Fach 1 (10,5 kg × 2) | 206 N | 567 mm | 0,44 mm | 1,89 mm | ✅ |
| Fachboden Fach 2 (1,5 kg × 2) | 29 N | 567 mm | 0,06 mm | 1,89 mm | ✅ |

Die verleimte Rückwand trägt die Hinterkante des Deckels zusätzlich mit. Sie ist hier nicht angesetzt.

## Kippsicherheit

Der Sockel steht 40 mm hinter der Korpuskante, das Polster 15 mm. Eine Last am Polsterrand liegt also 25 mm außerhalb der Standfläche.

| Fall | leer | mit Inventar |
|---|---:|---:|
| Senkrechte Last auf der Längskante, ab der die Bank kippt | 295 kg | 705 kg |
| Senkrechte Last auf der Stirnkante, ab der die Bank kippt | 1.034 kg | 2.468 kg |
| Lehne 85°: waagerechter Zug/Druck nach hinten an der Lehnenoberkante (1.227 mm hoch), niemand sitzt | 207 N | 493 N |

Sitzt jemand auf dem Sitz, steigt der letzte Wert (leere Bank) auf ≈ 1.142 N. Beim Training ist das unkritisch. Die aufgestellte Lehne ist aber kein Griff zum Hochziehen, wenn die Bank leer ist.

## Transport

- Die Rollen sitzen verdeckt unter dem Korpusüberstand am rechten Ende und greifen ab ≈ 8,2° Neigung.
- Dazu das linke Ende unter dem Überstand fassen und ≈ 165 mm anheben.
- Dabei zu heben (halbes Gewicht): leer ≈ 23 kg, mit Inventar ≈ 55 kg → schwere Hanteln vorher herausnehmen.
