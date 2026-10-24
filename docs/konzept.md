# Konzept: Sitzbank, die zur Trainingsbank wird

## Die Idee

Ein Möbelstück, das im Alltag als Sitzbank im Flur, am Bettende oder im Wohnzimmer steht.
Zum Training nimmt man die Hanteln aus dem Stauraum, und die Bank ist eine stabile Flachbank.
Vorbild ist die [Technogym Bench](https://www.technogym.com/en-US/product/technogym-bench_DGY100.html):
Flachbank mit eingebautem Stauraum für Hanteln, Bänder und Matte.

## Macht das Sinn? Ja.

**Die Maße einer Sitzbank und einer Flachbank sind fast gleich.**

| | Sitzbank (Möbel) | Flachbank (Training) | Technogym Bench | **Dieser Entwurf** |
|---|---|---|---|---|
| Höhe | 43–47 cm | 42–45 cm (Wettkampfnorm IPF) | 45,5 cm | **45 cm** |
| Länge | 100–140 cm | 110–125 cm Polster | 112,9 cm | **120 cm** |
| Tiefe/Breite | 35–45 cm | 26–32 cm Polster | 37,6 cm | **40 cm** |

Weitere Gründe:

- **Ein Kasten ist steifer als ein Gestell.** Deckel, Rückwand, Boden und Wangen bilden eine geschlossene Box.
  Die Überschlagsrechnung ([berechnung.md](berechnung.md)) zeigt bei 120 kg mit Stoßfaktor 1,5 nur etwa 1 mm Durchbiegung.
- **Die Bank kann nicht kippen.** Die Seitenwangen stehen bündig mit den Außenkanten, und das Polster steht nicht über.
  Senkrechte Lasten liegen damit immer innerhalb der Standfläche. Bei vielen Trainingsbänken mit schmalem Fuß ist das nicht so.
- **Das Gewicht hilft.** Leer wiegt die Bank etwa 40 kg, mit Hanteln etwa 100 kg. Sie rutscht beim Hip Thrust oder beim Rudern nicht weg.
- **Der Stauraum löst das eigentliche Problem.** Hanteln liegen sonst sichtbar herum, hier sind sie hinter Türen verstaut.

### Zielkonflikte und wie der Entwurf sie löst

| Thema | Möbel will … | Training will … | Lösung |
|---|---|---|---|
| Polsterbreite | 40–45 cm, bequem | 28–32 cm, Schulterblätter frei beim Kurzhantel-Drücken | 40 cm als Kompromiss (Technogym 37,6 cm). Parameter `bank.tiefe` |
| Polsterhärte | weich | fest, stabile Kante | Schichtaufbau: 30 mm hart (RG 50+) + 20 mm mittel (RG 35–40) |
| Bezug | Stoff, Bouclé, Wolle | abwischbar, schweißfest | Kunstleder/Leder oder abwischbarer Möbelstoff (Outdoor-/Performance-Stoff). **Kein Bouclé.** |
| Optik | geschlossene Front | schneller Zugriff | 2 Schiebetüren, 2 Fächer: Eine Tür zur Seite schieben, dann liegt ein ganzes Fach frei |
| Feuchtigkeit | – | Schweiß, verschwitztes Zubehör | Lüftungsschlitze in den Türen, Hartwachsöl/Lack, Leim D3 |
| Verschieben | soll beweglich sein | darf nicht rutschen | Gummipads unter den Füßen. Zum Bewegen an einem Ende ankippen und auf den Rollen schieben (wie Technogym) |

### Grenzen

- **Nur Flachbank, keine verstellbare Schrägbank.** Die Technogym Bench ist auch nur flach.
  Eine klappbare Rückenlehne wäre eine mögliche Erweiterung in Phase 5.
- **Kein Langhantel-Bankdrücken.** Dafür fehlt die Ablage, und dafür ist die Bank auch nicht gedacht.
- **Keine Box Jumps auf das Polster.**

## Übungen, die die Bank können muss

Diese Liste dient als Prüfliste für Maße, Polster und Standfestigkeit.

| Übung | Anforderung an die Bank |
|---|---|
| Kurzhantel-Bankdrücken, Fliegende | Polster fest, Breite ≤ 40 cm, Länge ≥ 110 cm |
| Einarmiges Rudern | Knie und Hand stützen auf der Kante → Kante steif, Polster rutschfest |
| Hip Thrust | Rücken drückt waagerecht gegen die Kante → Bank darf nicht wandern (Gewicht + Gummipads) |
| Bulgarian Split Squat, Step-ups | Fuß steht auf der Kante → keine Kippgefahr, harter Schaum unten |
| Dips, erhöhte Liegestütze | Hände auf der Kante → Kante steif |
| Sitzendes Schulterdrücken, Bizeps-Curls | Sitzhöhe 45 cm |
| Crunches, Beinheben | Länge 120 cm |

## Aufbau

![Explosionsansicht](../renders/explosion.png)

| Bauteil | Funktion |
|---|---|
| **Polster** | 15 mm Trägerplatte + 50 mm Schaum + Bezug. Liegt auf 4 Zentrierbolzen und ist abnehmbar. Optional von unten mit Sterngriffschrauben gesichert |
| **Deckel** | 18 mm, liegt **auf** den Seitenwangen. Die Last geht so direkt über Druck in die Wangen, nicht über Leimfugen |
| **Seitenwangen** | stehen auf dem Boden (Füße vorne und hinten). Links ein Griffloch zum Ankippen |
| **Rückwand** | verleimt, steift den Kasten gegen seitliches Verschieben aus (Rudern, Hip Thrust) |
| **Führungsleiste (Buche)** | unter dem Deckel vorne. Trägt die oberen Laufnuten der Türen und versteift die Vorderkante |
| **Mittelwand + Fachböden** | 2 Fächer mit je 2 Ebenen. Schweres unten. Fachböden liegen auf Bodenträgern und sind mit Filz/Kork belegt |
| **Schiebetüren** | 12 mm, mit Lüftungsschlitzen. Zum Einsetzen in die obere Nut hochschieben und unten absetzen; keine Beschläge nötig |
| **Boden + Sockelblenden** | Boden mit unteren Laufnuten. Die vordere Blende ist zurückgesetzt, damit die Fersen beim Sitzen Platz haben |
| **Rollen** | 2 Stück an der rechten Stirnseite, 4 mm über dem Boden. Sie greifen erst, wenn man links anhebt |

Stauraum mit dem Technogym-Inventar (Hantelmaße geschätzt, siehe [berechnung.md](berechnung.md)):

![Stauraum](../renders/stauraum.png)

## Material

| Option | Optik | Vorteile | Nachteile |
|---|---|---|---|
| **Birke Multiplex 18 mm** (Standard im Modell) | hell, sichtbare Schichtkanten, skandinavisch | formstabil, sehr fest, einfach zu verarbeiten | Kanten muss man mögen |
| Eiche-furniertes Multiplex/MDF + Anleimer | wie Massivholz | edel, formstabil | Anleimer an allen sichtbaren Kanten nötig, teurer |
| Eiche massiv (Leimholz) | klassisch | sehr wertig | arbeitet quer zur Faser (bei 40 cm Breite 2–3 mm), aufwendigere Konstruktion, teuer |
| Lackiertes MDF | farbig, grifflos-modern | günstig, glatt | schwer, empfindliche Kanten, schlechte Schraubhaltung |

## Fertigung

- **Selbst bauen:** Tauch- oder Tischkreissäge, Oberfräse (Nuten, Schlitze, Griffloch), Dübel- oder Dominofräse, Zwingen.
- **Zuschnitt bestellen:** Holzhandel oder Online-Zuschnitt nach der [Stückliste](stueckliste.md); Nuten und Schlitze selbst fräsen.
- **CNC-Service/Schreiner:** Das parametrische Modell lässt sich als DXF für den CNC-Zuschnitt exportieren (Phase 2).

## Referenz: Technogym Bench

Daten laut Händlerangaben (Technogym selbst war beim Abruf nicht erreichbar):

- 1129 × 376 × 455 mm, leer 35,2 kg, mit Zubehör 98,8 kg, max. Nutzergewicht 120 kg
- Zubehör: 5 Paar Kurzhanteln (2,5 / 3,5 / 5 / 7,5 / 10 kg), 3 Widerstandsbänder, 3 Paar Knuckles (0,45 / 0,8 / 1,2 kg), Trainingsmatte
- Halterungen mit Abstandshaltern gegen eingeklemmte Finger, Rollen an einer Stirnseite

Quellen: [Winnings](https://www.winnings.com.au/p/technogym-multifunctional-bench-dgy100),
[Northern Fitness](https://www.northernfitness.ca/products/technogym-bench),
[ArchiPro](https://archipro.com.au/product/technogym-bench-workout-bench-technogym)
