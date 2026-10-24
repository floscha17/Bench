# Konzept: Wohnbank mit Trainingsfunktion

## Die Idee

Ein hochwertiges Möbel aus Eiche und Cognac-Leder für das Ende eines 180-cm-Betts.
Im Alltag ist es eine Sitzbank. Zum Training nimmt man die selbstgebauten Hanteln heraus, rollt die Bank vom Bett weg und stellt die Polster an:
die Rückenlehne auf 15°, 30°, 45° oder 60°, den Sitz auf 10° oder 15°.

## Entwicklung: Bildentwurf → Studio-Vorentwurf → Modell

1. **[Bildentwurf](bildentwurf.png):** Gestaltung mit gerundeten Ecken, Lamellenfront, Polsterwanne, schwarzen Stützen und Bronze-Akzent.
2. **[Studio-Vorentwurf V01](vorentwurf-studio.pdf)** (24.10.2026): legt Maße, Verstellbereiche, Tragprinzip, Rollfront, Hantelaufnahmen und Fahrwerk fest. Besprechungsgrundlage, keine Fertigungsfreigabe.
3. **Dieses Modell:** setzt den Vorentwurf parametrisch um und rechnet nach, ob Mechanik, Stauraum, Durchbiegung und Kippsicherheit aufgehen.

| Möbel | Training |
|---|---|
| ![Bank als Möbel](../renders/moebel.png) | ![Training](../renders/training.png) |

### Was aus dem Vorentwurf übernommen ist und wo das Modell abweicht

| Vorentwurf | Umsetzung im Modell | |
|---|---|---|
| Außen 1200 × 430 × 460, Sockel 70 + Korpus 320 + Polster 70 | 1200 × 430 × **450**: Sockel 70 + Korpus **310** + Polster 70. 450 mm ist die Obergrenze der Wettkampfnorm für Flachbänke (deine Wahl) | angepasst |
| Lehne 0/15/30/45/60°, Sitz 0/10/15° | genau so | ✓ |
| Polster 820 + 10 Fuge + 330, Rand je 20 | 810 + **16** + 330, Rand 19 + 3 Luft. Die Fuge muss die gemeinsame Drehachse aufnehmen, siehe unten | angepasst |
| Polsterbreite 390 | **368**: Vorn und hinten bleibt je ein 12-mm-Spalt für Gelenkkonsolen und Laschen. Technogym Bench: 376 | angepasst, Liegeprobe |
| Beide Träger an einem gemeinsamen inneren Metallrahmen | Innenrahmen aus Rechteckrohr: 2 Längsrohre in der Wanne, 6 Stützen, Querrohre, 4 Hanteltraversen, Stellfüße an den Eckstützen | ✓ |
| Quer abgestützte, formschlüssig verriegelnde Beschläge statt Möbelklappenstütze | Je Polster eine Gleitstütze aus 2 Flachstahlbeinen mit Quersteg. Ihr Fuß läuft in C-Schienen, ein federnder Indexbolzen Ø 10 rastet in jeder Arbeitsstellung ein | ✓ |
| Drehpunkt in der Funktionsskizze unten am Polster | Gemeinsame Achse **oben**, 12 mm unter der Oberfläche. Mit der Achse unten würden die Polsterkanten bei 60° rund 61 mm in die Fuge wandern | abweichend |
| – | Flachstellung über Endanschlag + Kugelschnäpper statt eigenem Rastloch. Ein Loch für flach läge nur gut 10 mm neben dem 15°-Loch | Detail |
| Rollfront nach links um die Ecke, Rücklaufkanal hinten | Tasche links 100 mm, Laufnuten mit mindestens R 50, Rücklauf hinter dem Nutzraum. Speicherweg 1.331 mm für eine 1.060 mm lange Tür | ✓ |
| Hanteln einzeln, gepolstert, verriegelbar, an Metalltraversen | 10 Einzelaufnahmen auf 4 Flachstahltraversen in 2 Ebenen, schwere unten, lösbarer Sicherungsbügel | ✓ |
| Rollenrahmen, 4 Lenkrollen, versenktes Fußpedal rechts, 5–10 mm Fußfreiheit | 2 gekoppelte Exzenterwellen, Hub 8 mm, Totpunktrast in beiden Lagen, Bronze-Pedal | ✓ |
| Formstabile Plattenkonstruktion mit Eichenoberfläche | Furnierte Platten 19 mm, Rundungen formverleimt, Lamellen, Frontleisten und Kanten Eiche massiv | ✓ |
| Angebot getrennt nach Holzbau, Polster, Metallbau/Beschlägen, Fahrwerk | [Stückliste](stueckliste.md) und Kosten genau so gegliedert | ✓ |
| Vor der Fertigung klären (6 Punkte), Spindelantrieb als Option | in die [Schreiner-Unterlagen](schreiner.md) übernommen, Spindel als Kostenoption | ✓ |

## Macht das Sinn? Ja.

| | Bank am Bettende | Trainingsbank | Technogym Bench | **Dieser Entwurf** |
|---|---|---|---|---|
| Höhe | 42–48 cm, unter der Matratzenoberkante | 42–45 cm (Wettkampfnorm IPF) | 45,5 cm | **45 cm** |
| Länge | ca. ⅔ bis ¾ der Bettbreite (bei 180 cm: 120–135 cm) | 110–125 cm | 112,9 cm | **120 cm** |
| Polsterbreite | 35–45 cm | 26–32 cm | 37,6 cm | **36,8 cm** |
| Sitz / Lehne | – | ca. 30–40 / 75–95 cm | – | **33 / 81 cm** |

- **Der Stahlrahmen trägt, das Holz verkleidet.** Polster, Hanteln und Füße hängen am Innenrahmen. Die Verkleidung bleibt frei von Trainingslasten und kann als ruhige Plattenkonstruktion gebaut werden ([berechnung.md](berechnung.md)).
- **Die Bank kippt praktisch nicht.** Erst ab rund 314 kg senkrecht auf dem äußersten Lehnenende würde sie leer kippen, mit Hanteln ab rund 600 kg.
- **Das Gewicht hilft.** Leer wiegt die Bank etwa 71 kg, mit Hanteln und Zubehör etwa 135 kg. Sie wandert beim Training nicht.
- **Der Stauraum löst das eigentliche Problem.** Im Schlafzimmer liegen keine Hanteln herum.

## Am Bettende

| Thema | Lösung |
|---|---|
| Länge | 120 cm bei einem 180-cm-Bett, also je Seite 30 cm Luft |
| Höhe | 45 cm, unter der üblichen Matratzenoberkante (50–65 cm) |
| Ausrichtung | Rollfront zum Raum, Rückseite zum Bett. Die Rückwand ist furniert, weil man sie vom Bett aus sieht, und bekommt eine Wartungsöffnung |
| Zum Training abrücken | Bronze-Pedal rechts im Sockel treten: Der Rollenrahmen senkt sich, die Füße heben 8 mm ab, die Bank rollt ca. 60 cm vom Bett weg. Pedal zurück, dann steht sie wieder auf den Füßen. Den Platz braucht man, weil die Ellbogen beim Drücken unter Polsterhöhe gehen und auf der Schrägbank ein Fuß neben der Bank steht |
| Beim Verschieben | Polster flach, Rollfront zu, niemand auf der Bank |

## Leder: die hochwertigste Wahl, aber die richtige Sorte

Echtes Leder ist das hochwertigste Polstermaterial. Bei einer Trainingsbank kommt es aber auf die Sorte an, weil Schweiß Salz und Säure enthält:

| Lederart | Optik | Für diese Bank |
|---|---|---|
| Anilinleder | am natürlichsten, offenporig | ✗ Schweiß und Wasser hinterlassen Flecken |
| Nubuk, Velours | samtig | ✗ saugt Schweiß auf |
| **Semianilin** | natürlich, leicht pigmentiert | ✓ guter Kompromiss |
| **Pigmentiertes Vollnarbenleder** | gleichmäßige Farbe, matt | ✓ am robustesten, abwischbar, farbstabil |

**Empfehlung:** vollnarbiges Rindleder in Cognac, pigmentiert oder Semianilin mit Schutzfinish, 1,2–1,5 mm, mit Kedernaht. Nach dem Training feucht abwischen, zweimal im Jahr pflegen.
Bezug und Polster werden austauschbar gebaut (Wunsch aus dem Vorentwurf).

## Mechanik

![Verstellbereich](../renders/verstellung.png)

| Lehne | Sitz | Wofür |
|---|---|---|
| 0° | 0° | Sitzbank, Kurzhantel-Bankdrücken, Rudern einarmig, Hip Thrust |
| 15° / 30° | 10° | Schrägbankdrücken (obere Brust), Fliegende schräg |
| 45° | 10° / 15° | steiles Schrägbankdrücken, Incline Curls |
| 60° | 15° | Schulterdrücken mit leichter Rücklage, Curls mit Rückenlehne |

Für Schulterdrücken ganz aufrecht (80–90°) ist die Bank nicht ausgelegt. Das entspricht dem Verstellbereich des Vorentwurfs.

**Drehachse:** Lehne und Sitz drehen um eine gemeinsame Achse M10 in der Mitte der 16-mm-Fuge, 12 mm unter der Polsteroberfläche, 840 mm vom linken Ende.
Getragen wird sie von zwei schlanken Gelenkkonsolen, die vorn und hinten im Spalt neben den Polstern auf die Längsrohre geschweißt sind.
Weil die Achse fast auf Polsterhöhe liegt, bleibt die Fuge in jeder Stellung schmal: mindestens 5,3 mm zwischen den Polsterkanten, auch bei Lehne 60° und Sitz 15° gleichzeitig.
Zwei getrennte Achsen gingen bei dieser Fuge nicht, weil zwei Bolzen M10 mehr als 16 mm Abstand brauchen.

**Verriegelung:** Unter jedem Polster sitzt eine Gleitstütze aus zwei Flachstahlbeinen 25 × 8 mit Quersteg. Ihr Fuß gleitet in zwei C-Schienen auf dem Wannenboden.
In jeder Arbeitsstellung rastet ein federnder Indexbolzen Ø 10 je Bein in ein Loch der Schiene ein: formschlüssig, nicht nur durch Reibung.
Die beiden Bolzen einer Stütze werden gemeinsam mit einem Zugknopf gelöst. Flach liegt das Polster auf dem Rahmen, der Gleitschuh steht am Endanschlag, ein Kugelschnäpper hält ihn.
Die Lochpositionen stehen in [gleitschienen.svg](zeichnungen/gleitschienen.svg) und sind das kritische Maß für den Metallbau.

**Belastung:** Gerechnet sind 120 kg Nutzer mit Stoßfaktor 1,5, in zwei Lastfällen: Gewicht senkrecht nach unten und kräftiges Zurücklehnen senkrecht gegen die Lehne.
Die Lehnenstütze trägt bis 2,8 kN (bei 15°) und knickt erst bei rund dem Zehnfachen. Die Indexbolzen sind mit unter 10 N/mm² Scherspannung kaum ausgelastet.
Den verbindlichen Nachweis übernimmt der Metallbau bzw. Beschlaglieferant, wie im Vorentwurf gefordert.

## Was das Design hochwertig macht

| Detail | Umsetzung |
|---|---|
| **Weiche Form** | Senkrechte Ecken R 70, formverleimt und stehend furniert, die Maserung läuft um die Rundung |
| **Verschwindende Rollfront** | Senkrechte Eichenlamellen ohne Griffe und Beschläge. Offen läuft die Front links um die Ecke und hinten zurück, der Innenraum liegt ganz frei |
| **Polsterwanne** | Die Polster liegen in einem 25 mm hohen Eichenrand, die Polsterplatte zeigt eine sichtbare Eichenkante |
| **Leder** | Cognac, vollnarbig, mit Kedernaht |
| **Schwebender Sockel** | Eichenzarge 25 mm zurückgesetzt, schwarze Füße, Rollen und Rahmen unsichtbar |
| **Bronze-Akzent** | Fußpedal vorn rechts im Sockel |
| **Passende Hanteln** | Schwarze Stahlköpfe und Eichengriffe in gepolsterten Einzelaufnahmen ([hanteln.md](hanteln.md)) |
| **Gelenk** | Im Spalt zwischen den Polstern sichtbar. Schwarz wie die Hanteln oder bronziert wie das Pedal: am Muster entscheiden |

Eine dunkle Alternative (Nussbaum, schwarzes Leder, Messing) ist im Modell mit `farbschema = "nussbaum"` umschaltbar.

## Aufbau

![Tragwerk](../renders/tragwerk.png)

| Bauteil | Funktion |
|---|---|
| **Innenrahmen** (Metallbau) | 2 Längsrohre 50 × 25 × 3 in der Wanne tragen Polster, Gelenk und Gleitschienen. 6 Stützen 30 × 30 innerhalb der Sockelzarge, Querrohre, Stellfüße an den 4 Eckstützen |
| **Hantelaufnahmen** | 4 Flachstahltraversen 30 × 8 hochkant zwischen den Stützen, je Hantel 2 gepolsterte Auflagen am Griff, seitliche Anschläge, Sicherungsbügel |
| **Verkleidung** (Schreiner) | Wannenboden, Boden, Stirnseiten, Rückwand aus eichefurnierten Platten 19 mm, 4 formverleimte Eckrundungen, Frontleisten Eiche massiv. Trägt nicht mit |
| **Rollfront** | 54 Eichenlamellen 18 × 14 mm auf flexiblem Träger, oben und unten in 8 × 8 mm Nuten geführt |
| **Innenraum** | Tasche 100 mm, Hantelbereich 660 mm mit 2 Ebenen, Zubehör 378 mm mit Fachboden. Trennwände 12 mm, nicht tragend |
| **Polster** | Multiplex 18 mit Eichenkante, 52 mm Schaum, Leder. Unter der Lehne 2 Eichenrippen |
| **Mechanik** | Gemeinsame Achse auf 2 Gelenkkonsolen, 4 Laschen, 2 Gleitstützen, 4 Gleitschienen, 4 Indexbolzen |
| **Fahrwerk** | Geführter Rollenrahmen, 2 gekoppelte Exzenterwellen, 4 Lenkrollen Ø 50, Bronze-Pedal. Option: Spindelantrieb mit Taster |

![Explosionsansicht](../renders/explosion.png)

Stauraum (Rollfront offen):

![Stauraum](../renders/stauraum.png)

## Fertigung und Kosten

Wie im Vorentwurf vier Gewerke, die Unterlagen stehen in [schreiner.md](schreiner.md), druckfertig als [schreiner-mappe.pdf](schreiner-mappe.pdf):

- **Holzbau:** Verkleidung, Rollfront, Polsterplatten, Oberfläche, Endmontage.
- **Polster:** Schaum und Leder auf den Polsterplatten.
- **Metallbau und Beschläge:** Innenrahmen, Gelenk, Gleitstützen, Gleitschienen, Hantelaufnahmen.
- **Fahrwerk:** Rollenrahmen mit Pedal.
- **Hanteln:** selbst bzw. Dreherei ([hanteln.md](hanteln.md)).

Kosten grob **6.600–12.200 €**, dazu die Hanteln für ca. 460–730 € (Aufschlüsselung in der [Stückliste](stueckliste.md)).
Der Stahlrahmen und die verriegelnden Beschläge machen die Bank teurer als eine reine Holzlösung, dafür trägt sie Trainingslasten sauber und nachweisbar ab.
Die Angebote werden die Zahl genauer zeigen.

## Referenz: Technogym Bench

Laut Händlerangaben: 1129 × 376 × 455 mm, leer 35,2 kg, max. Nutzergewicht 120 kg, 5 Paar Kurzhanteln 2,5–10 kg, Bänder, Knuckles, Matte, nur Flachbank.
Quellen: [Winnings](https://www.winnings.com.au/p/technogym-multifunctional-bench-dgy100),
[Northern Fitness](https://www.northernfitness.ca/products/technogym-bench),
[ArchiPro](https://archipro.com.au/product/technogym-bench-workout-bench-technogym)
