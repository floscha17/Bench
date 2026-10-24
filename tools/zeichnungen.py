"""Bemaßte Maßskizzen als SVG für Schreiner, Metallbau und Dreherei.

Wird von build.py aufgerufen; alle Maße kommen aus denselben abgeleiteten Werten wie Modell und Stückliste.
"""

import math
from pathlib import Path

STIL = """
  .bg { fill: #ffffff; }
  .k { fill: none; stroke: #1d1d1b; stroke-width: 1.2; }
  .d { fill: none; stroke: #1d1d1b; stroke-width: 0.8; stroke-dasharray: 5 3; }
  .holz { fill: #ead9bd; stroke: #1d1d1b; stroke-width: 1.2; }
  .innen { fill: #f4ead8; stroke: #1d1d1b; stroke-width: 0.9; }
  .dunkel { fill: #3a3633; stroke: #1d1d1b; stroke-width: 1; }
  .leder { fill: #c0784a; stroke: #1d1d1b; stroke-width: 1.2; }
  .stahl { fill: #55585c; stroke: #1d1d1b; stroke-width: 1; }
  .m { stroke: #b3261e; stroke-width: 0.7; fill: none; }
  .mt { fill: #b3261e; font: 11px sans-serif; }
  .t { fill: #1d1d1b; font: 12px sans-serif; }
  .tk { fill: #555; font: 10px sans-serif; }
  .titel { fill: #1d1d1b; font: bold 18px sans-serif; }
  .ut { fill: #1d1d1b; font: bold 13px sans-serif; }
"""


def zahl(x):
    s = f"{x:.1f}".rstrip("0").rstrip(".")
    return s.replace(".", ",")


class Blatt:
    def __init__(self, breite, hoehe, titel, untertitel=""):
        self.b, self.h = breite, hoehe
        self.teile = [f'<rect class="bg" width="{breite}" height="{hoehe}"/>',
                      f'<text class="titel" x="20" y="32">{titel}</text>']
        if untertitel:
            self.teile.append(f'<text class="tk" x="20" y="50">{untertitel}</text>')

    def roh(self, s):
        self.teile.append(s)

    def speichern(self, pfad):
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.b}" height="{self.h}" '
               f'viewBox="0 0 {self.b} {self.h}"><style>{STIL}</style>' + "".join(self.teile) + "</svg>\n")
        Path(pfad).write_text(svg)


class Ansicht:
    """Zeichenfläche mit Maßstab; Objektkoordinaten (u nach rechts, v nach oben) in mm."""

    def __init__(self, blatt, ox, oy, massstab, titel=None):
        self.bl, self.ox, self.oy, self.s = blatt, ox, oy, massstab
        if titel:
            blatt.roh(f'<text class="ut" x="{ox}" y="{oy + 34}">{titel}</text>')

    def p(self, u, v):
        return self.ox + u * self.s, self.oy - v * self.s

    def rect(self, u, v, w, h, cls="k"):
        x, y = self.p(u, v + h)
        self.bl.roh(f'<rect class="{cls}" x="{x:.1f}" y="{y:.1f}" width="{w * self.s:.1f}" height="{h * self.s:.1f}"/>')

    def linie(self, u1, v1, u2, v2, cls="k"):
        x1, y1 = self.p(u1, v1)
        x2, y2 = self.p(u2, v2)
        self.bl.roh(f'<line class="{cls}" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"/>')

    def kreis(self, u, v, r, cls="k"):
        x, y = self.p(u, v)
        self.bl.roh(f'<circle class="{cls}" cx="{x:.1f}" cy="{y:.1f}" r="{r * self.s:.1f}"/>')

    def poly(self, punkte, cls="k"):
        pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in (self.p(u, v) for u, v in punkte))
        self.bl.roh(f'<polygon class="{cls}" points="{pts}"/>')

    def text(self, u, v, txt, cls="t", anker="start", dx=0, dy=0):
        x, y = self.p(u, v)
        self.bl.roh(f'<text class="{cls}" x="{x + dx:.1f}" y="{y + dy:.1f}" text-anchor="{anker}">{txt}</text>')

    def mass_h(self, u1, u2, v, abstand, txt=None, ref=None):
        """Waagerechtes Maß zwischen u1 und u2; Maßlinie `abstand` px unter (+) bzw. über (−) der Höhe v."""
        x1, y = self.p(u1, v)
        x2, _ = self.p(u2, v)
        ym = y + abstand
        r = self.p(0, ref)[1] if ref is not None else y
        for x in (x1, x2):
            self.bl.roh(f'<line class="m" x1="{x:.1f}" y1="{r:.1f}" x2="{x:.1f}" y2="{ym + (4 if abstand > 0 else -4):.1f}"/>')
        self.bl.roh(f'<line class="m" x1="{x1:.1f}" y1="{ym:.1f}" x2="{x2:.1f}" y2="{ym:.1f}"/>')
        for x in (x1, x2):
            self.bl.roh(f'<line class="m" x1="{x - 3:.1f}" y1="{ym + 3:.1f}" x2="{x + 3:.1f}" y2="{ym - 3:.1f}"/>')
        t = txt if txt is not None else zahl(abs(u2 - u1))
        self.bl.roh(f'<text class="mt" x="{(x1 + x2) / 2:.1f}" y="{ym - 3:.1f}" text-anchor="middle">{t}</text>')

    def mass_v(self, v1, v2, u, abstand, txt=None, ref=None):
        """Senkrechtes Maß zwischen v1 und v2; Maßlinie `abstand` px rechts (+) bzw. links (−) von u."""
        x, y1 = self.p(u, v1)
        _, y2 = self.p(u, v2)
        xm = x + abstand
        r = self.p(ref, 0)[0] if ref is not None else x
        for y in (y1, y2):
            self.bl.roh(f'<line class="m" x1="{r:.1f}" y1="{y:.1f}" x2="{xm + (4 if abstand > 0 else -4):.1f}" y2="{y:.1f}"/>')
        self.bl.roh(f'<line class="m" x1="{xm:.1f}" y1="{y1:.1f}" x2="{xm:.1f}" y2="{y2:.1f}"/>')
        for y in (y1, y2):
            self.bl.roh(f'<line class="m" x1="{xm - 3:.1f}" y1="{y + 3:.1f}" x2="{xm + 3:.1f}" y2="{y - 3:.1f}"/>')
        t = txt if txt is not None else zahl(abs(v2 - v1))
        ym = (y1 + y2) / 2
        self.bl.roh(f'<text class="mt" x="{xm - 4:.1f}" y="{ym:.1f}" text-anchor="middle" '
                    f'transform="rotate(-90 {xm - 4:.1f} {ym:.1f})">{t}</text>')


def uebersicht(ziel, p, d):
    L, D, H, t = d["L"], d["D"], d["H"], d["t"]
    k, po = p["korpus"], p["polster"]
    se, sh = k["sockel_einzug"], k["sockel_hoehe"]
    s = 0.62
    bl = Blatt(1100, 1290, "Übersicht – Hauptmaße", "Maße in mm. Lehne flach.")

    # Vorderansicht
    a = Ansicht(bl, 140, 420, s, None)
    bl.roh(f'<text class="ut" x="140" y="90">Vorderansicht (Raumseite, Türen geschlossen)</text>')
    a.rect(se, 0, L - 2 * se, sh, "dunkel")
    a.rect(0, sh, L, d["korpus_h"], "holz")
    a.rect(t, d["boden_z1"], d["innen_l"], d["innen_h"], "innen")
    for i, x0 in enumerate(d["tuer_x0"]):
        a.rect(x0, d["tuer_z0"], d["tuer_l"], d["tuer_h"], "k" if i % 2 == 0 else "d")
    for x in d["fach_x0"][1:]:
        a.linie(x - d["ti"] / 2, d["boden_z1"], x - d["ti"] / 2, d["deckel_z0"], "d")
    a.rect(d["sitz_x0"] + 25, d["deckel_z1"], po["sitz_laenge"] - 50, po["schattenfuge"], "dunkel")
    a.rect(d["leiste_x0"], d["deckel_z1"], d["leiste_x1"] - d["leiste_x0"], po["schattenfuge"], "dunkel")
    a.rect(d["sitz_x0"], d["polster_z0"], po["sitz_laenge"], d["polster_h"], "leder")
    a.rect(d["lehne_x0"], d["polster_z0"], d["lehne_l"], d["polster_h"], "leder")
    a.kreis(d["achse_x"], d["achse_z"], 6, "stahl")
    a.mass_h(0, L, H, -40, ref=H)
    a.mass_h(0, d["sitz_x0"], H, -18)
    a.mass_h(d["sitz_x0"], d["sitz_x1"], H, -18)
    a.mass_h(d["sitz_x1"], d["lehne_x0"], H, -18)
    a.mass_h(d["lehne_x0"], d["lehne_x1"], H, -18)
    a.mass_h(0, d["achse_x"], 0, 26, f"Drehachse {zahl(d['achse_x'])}", ref=d["achse_z"])
    a.mass_h(0, se, 0, 48)
    a.mass_v(0, H, L, 70)
    for z0, z1 in ((0, sh), (sh, d["deckel_z1"]), (d["deckel_z1"], d["polster_z0"]), (d["polster_z0"], H)):
        a.mass_v(z0, z1, L, 34)
    a.text(L / 2, d["boden_z1"] + d["innen_h"] / 2, f"{d['n_tuer']} Schiebetüren aus Lamellen, je {zahl(d['tuer_l'])} breit",
           "tk", "middle")

    # Draufsicht (ohne Polster)
    a = Ansicht(bl, 140, 850, s, None)
    bl.roh(f'<text class="ut" x="140" y="540">Draufsicht ohne Polster (Bettseite oben)</text>')
    a.rect(0, 0, L, D, "holz")
    a.rect(d["sitz_x0"], d["pad_y0"], po["sitz_laenge"], d["pad_b"], "d")
    a.rect(d["lehne_x0"], d["pad_y0"], d["lehne_l"], d["pad_b"], "d")
    a.rect(d["sitz_x0"] + 25, d["pad_y0"] + 25, po["sitz_laenge"] - 50, d["pad_b"] - 50, "k")
    for y in d["leiste_y0"]:
        a.rect(d["leiste_x0"], y, d["leiste_x1"] - d["leiste_x0"], p["schraegbank"]["leiste_breite"], "dunkel")
    for y in (d["pad_y0"] - 9, D - d["pad_y0"] + 4):
        a.rect(d["achse_x"] - 30, y, 40, 5, "stahl")
    a.text(d["leiste_x0"] + 10, D / 2, "Rastleisten, Maße siehe rastleiste.svg", "tk")
    a.text(d["sitz_x0"] + 35, D / 2, "Distanzrahmen Sitz", "tk")
    a.mass_v(0, D, L, 40)
    a.mass_v(0, d["pad_y0"], L, 14)
    a.mass_v(D - d["pad_y0"], D, L, 14)
    a.mass_v(0, d["leiste_y0"][0], 0, -14)
    a.mass_v(d["leiste_y0"][1] + p["schraegbank"]["leiste_breite"], D, 0, -14)
    a.mass_h(d["achse_x"], d["leiste_x0"], 0, 22)
    a.mass_h(d["leiste_x0"], d["leiste_x1"], 0, 22)
    a.text(-40, 0, "vorne / Raum", "tk", "end", dy=4)
    a.text(-40, D, "hinten / Bett", "tk", "end", dy=4)

    # Seitenansicht
    a = Ansicht(bl, 140, 1230, s, None)
    bl.roh(f'<text class="ut" x="140" y="925">Seitenansicht von rechts</text>')
    a.rect(se, 0, D - 2 * se, sh, "dunkel")
    a.rect(0, sh, D, d["korpus_h"], "holz")
    a.rect(d["pad_y0"], d["polster_z0"], d["pad_b"], d["polster_h"], "leder")
    a.rect(d["pad_y0"] + 25, d["deckel_z1"], d["pad_b"] - 50, po["schattenfuge"], "dunkel")
    a.kreis(D - se / 2, p["rollen"]["durchmesser"] / 2 + p["rollen"]["bodenfreiheit"], p["rollen"]["durchmesser"] / 2, "stahl")
    a.mass_h(0, D, 0, 18)
    a.mass_v(0, H, D, 30)
    a.text(D + 70, 40, "Rolle verdeckt unter dem hinteren Überstand", "tk")
    bl.speichern(ziel / "uebersicht.svg")


def schnitt(ziel, p, d):
    D, H, t = d["D"], d["H"], d["t"]
    k, po, tu, sb = p["korpus"], p["polster"], p["tueren"], p["schraegbank"]
    se, sh = k["sockel_einzug"], k["sockel_hoehe"]
    s = 1.55
    bl = Blatt(1200, 920, "Querschnitt durch ein Fach",
               "Maße in mm. Schnitt quer zur Bank im Bereich der Rückenlehne, links vorne (Raum), rechts hinten (Bett).")
    a = Ansicht(bl, 380, 790, s)
    a.rect(se, 0, t, sh, "dunkel")
    a.rect(D - se - t, 0, t, sh, "dunkel")
    a.rect(0, sh, D, t, "holz")
    a.rect(0, d["deckel_z0"], D, t, "holz")
    a.rect(d["rueck_y0"], d["boden_z1"] - 10, d["tr"], d["innen_h"] + 20, "innen")
    if k["fachboden"]:
        a.rect(d["fach_y0"] + 5, d["fachboden_z0"], d["fach_tiefe"] - 5, d["ti"], "innen")
    for i, y0 in enumerate(d["tuer_y0"]):
        a.rect(y0, d["tuer_z0"], tu["lamelle_dicke"], d["tuer_h"], "holz")
        a.rect(y0 + tu["lamelle_dicke"], d["tuer_z0"] + 20, tu["traverse_dicke"], 40, "dunkel")
        a.rect(y0 + tu["lamelle_dicke"], d["tuer_z0"] + d["tuer_h"] - 40, tu["traverse_dicke"], 40 + tu["nut_oben"] - 2, "dunkel")
        a.rect(y0 + tu["lamelle_dicke"] - 0.5, d["deckel_z0"], tu["traverse_dicke"] + 1, tu["nut_oben"], "k")
        a.rect(y0 + tu["lamelle_dicke"] - 0.5, d["boden_z1"] - 5, tu["traverse_dicke"] + 1, 5, "k")
    for y in d["leiste_y0"]:
        a.rect(y, d["deckel_z1"], sb["leiste_breite"], po["schattenfuge"], "dunkel")
    for y in d["rippe_y0"]:
        a.rect(y, d["polster_z0"] - sb["rippe_hoehe"], sb["rippe_breite"], sb["rippe_hoehe"], "holz")
    a.rect(d["pad_y0"], d["polster_z0"], d["pad_b"], po["platte"], "innen")
    a.rect(d["pad_y0"], d["polster_z0"] + po["platte"], d["pad_b"], po["schaum"], "leder")
    a.rect(D - se / 2 - 7.5, p["rollen"]["bodenfreiheit"], 15, p["rollen"]["durchmesser"], "stahl")
    # Höhenkette rechts
    kette = [0, sh, d["boden_z1"]]
    if k["fachboden"]:
        kette += [d["fachboden_z0"], d["fachboden_z1"]]
    kette += [d["deckel_z0"], d["deckel_z1"], d["polster_z0"], d["polster_z0"] + po["platte"], H]
    for z0, z1 in zip(kette, kette[1:]):
        a.mass_v(z0, z1, D, 40, ref=D)
    a.mass_v(0, H, D, 90, ref=D)
    # Tiefenkette unten und oben
    a.mass_h(0, se, 0, 22)
    a.mass_h(D - se, D, 0, 22)
    kette = [0, d["tuer_y0"][0], d["tuer_y0"][1], d["fach_y0"], d["rueck_y0"], D]
    for y0, y1 in zip(kette, kette[1:]):
        a.mass_h(y0, y1, 0, 50, txt=f"Fachtiefe {zahl(d['fach_tiefe'])}" if y0 == d["fach_y0"] else None)
    a.mass_h(0, D, 0, 78)
    a.mass_h(0, d["pad_y0"], H, -24, ref=H)
    a.mass_h(d["pad_y0"], D - d["pad_y0"], H, -24, ref=H)
    # Beschriftung links
    notizen = [
        (H - po["schaum"] / 2, "Leder + Schaum 30 hart / 20 mittel"),
        (d["polster_z0"] + po["platte"] / 2, f"Polsterplatte Multiplex {po['platte']}"),
        (d["deckel_z1"] + po["schattenfuge"] / 2, "Schattenfuge: Rastleisten (schwarz) und Eichenrippen der Lehne"),
        (d["deckel_z0"] + t / 2, f"Deckel Eiche massiv {t}, Führungsnuten {tu['nut_oben']} tief"),
        ((d["fachboden_z1"] + d["deckel_z0"]) / 2 if k["fachboden"] else d["deckel_z0"] - 40, "obere Ebene"),
        ((d["boden_z1"] + (d["fachboden_z0"] or d["deckel_z0"])) / 2, f"untere Ebene {k['fach_unten']} (Hanteln)"),
        (sh + t / 2, f"Boden Eiche massiv {t}, Laufnuten 5 tief"),
        (sh / 2, f"Sockel schwarz, {se} zurückgesetzt"),
    ]
    for z, txt in notizen:
        a.text(-12, z, txt, "tk", "end", dy=4)
    a.text(d["fach_y0"] + 10, d["boden_z1"] + 20, "← Lamellentüren auf 2 Spuren", "tk")
    a.text(d["rueck_y0"] - 4, d["boden_z1"] + 20, "Rückwand in Nut", "tk", "end")
    bl.speichern(ziel / "schnitt.svg")


def rastleiste(ziel, p, d, rs, park):
    sb, po = p["schraegbank"], p["polster"]
    x0, x1 = d["leiste_x0"], d["leiste_x1"]
    hoehe, r = po["schattenfuge"], sb["buegel_d"] / 2
    s = 1.05
    bl = Blatt(1100, 600, "Rastleiste (2 Stück, spiegelgleich)",
               "Maße in mm ab Drehachse der Lehne. Eiche massiv, schwarz gebeizt, mit dem Deckel verleimt und verschraubt.")
    a = Ansicht(bl, 60 - (x0 - d["achse_x"]) * s + 20, 300, s)
    u0, u1 = x0 - d["achse_x"], x1 - d["achse_x"]
    a.rect(u0, 0, u1 - u0, hoehe, "dunkel")
    a.linie(0, -30, 0, hoehe + 60, "d")
    a.text(0, hoehe + 66, "Drehachse", "tk", "middle")
    marken = [(r_["n"], f"{r_['winkel']}°", sb["rast_tiefe"]) for r_ in rs if r_["ok"]] + [(park, "Park 0°", d["park_tiefe"])]
    marken.sort()
    for i, (n, lab, tiefe) in enumerate(marken):
        boden = hoehe - tiefe + r - r
        a.rect(n - r - 0.5, boden, 2 * r + 1, tiefe, "bg")
        a.kreis(n, hoehe - tiefe + r, r, "stahl")
        a.text(n, hoehe + (12 if i % 2 == 0 else 28), lab, "t", "middle")
        a.mass_h(0, n, 0, 28 + 18 * i, ref=hoehe - tiefe)
    a.mass_v(0, hoehe, u1, 24)
    a.mass_h(0, u0, hoehe, -30, ref=hoehe)
    a.mass_h(u0, u1, hoehe, -70, f"Leiste {zahl(u1 - u0)}", ref=hoehe)
    zeilen = [f"Rasten: Ø {sb['buegel_d'] + 1} halbrund, {sb['rast_tiefe']} tief (Parkrast {zahl(d['park_tiefe'])} tief, Langloch nach oben offen).",
              f"Lage quer: {zahl(d['leiste_y0'][0])} mm ab Vorderkante bzw. {zahl(d['D'] - d['leiste_y0'][1] - sb['leiste_breite'])} mm ab Hinterkante, Breite {sb['leiste_breite']}.",
              f"Drehachse liegt {zahl(d['achse_x'])} mm ab linker Stirnseite, {zahl(d['achse_z'] - d['deckel_z1'])} mm über dem Deckel.",
              "Beide Leisten gemeinsam bearbeiten (zusammengespannt), damit die Rasten exakt fluchten."]
    for i, z in enumerate(zeilen):
        bl.roh(f'<text class="t" x="40" y="{500 + i * 18}">{z}</text>')
    bl.speichern(ziel / "rastleiste.svg")


def metall(ziel, p, d):
    sb, po = p["schraegbank"], p["polster"]
    s = 1.6
    bl = Blatt(1100, 700, "Metallteile – Entwurfsmaße für den Metallbau",
               "Maße in mm. Stahl S235, schwarz pulverbeschichtet. Endgültige Fertigungszeichnung durch Metallbau nach Aufmaß am Korpus.")
    # Gelenkplatte Korpus: Achse über Deckel
    a = Ansicht(bl, 120, 330, s, None)
    bl.roh('<text class="ut" x="40" y="90">Gelenkplatte Korpus (2×, außen)</text>')
    hz = d["achse_z"] - d["deckel_z1"]
    a.poly([(-30, 0), (8, 0), (8, 6), (11, hz), (0, hz + 11), (-11, hz), (-30, 6)], "stahl")
    a.kreis(0, hz, 5.25, "bg")
    a.mass_v(0, hz, 11, 40, ref=0)
    a.mass_h(-30, 0, 0, 20)
    a.mass_h(0, 8, 0, 20)
    a.text(-30, -40, f"Dicke {sb['gelenkplatte']}, Bohrung Ø 10,5 für Bolzen M10,", "tk")
    a.text(-30, -50, "Fuß 90 mm unter den Sitz gekantet, 4 × M6 durch Deckel", "tk")
    # Gelenkplatte Lehne
    a = Ansicht(bl, 470, 330, s, None)
    bl.roh('<text class="ut" x="380" y="90">Gelenkplatte Lehne (2×, innen)</text>')
    hb = d["achse_z"] - d["polster_z0"]
    a.poly([(0, hb + 11), (-11, hb), (12, 0), (57, 0), (57, 4), (11, hb + 6)], "stahl")
    a.kreis(0, hb, 5.25, "bg")
    a.mass_v(0, hb, 57, 30, ref=0)
    a.mass_h(0, 57, 0, 20)
    a.text(-11, -40, "Lasche unter die Lehnenplatte gekantet,", "tk")
    a.text(-11, -50, "3 × Senkschraube in Einschlagmuttern", "tk")
    # Stütze
    a = Ansicht(bl, 720, 450, 0.55, None)
    bl.roh('<text class="ut" x="700" y="90">Klappstütze (1×, geschweißt)</text>')
    l, bb, b8 = sb["stuetze_laenge"], sb["bein_breite"], sb["bein_dicke"]
    y0, y1 = d["bein_y0"][0] - d["stab_y0"], d["bein_y0"][1] - d["stab_y0"]
    for y in (y0, y1):
        a.rect(y, 0, bb, l, "stahl")
        a.kreis(y + bb / 2, l, 4.25, "bg")
    a.rect(0, -sb["buegel_d"] / 2, d["stab_l"], sb["buegel_d"], "stahl")
    a.mass_v(0, l, y1 + bb, 30, f"{zahl(l)} Bohrung–Stabmitte", ref=y1 + bb / 2)
    a.mass_h(0, d["stab_l"], 0, 30, f"Querstab Ø {sb['buegel_d']} × {zahl(d['stab_l'])}")
    a.mass_h(y0, y1 + bb, l, -24, ref=l)
    a.text(0, -90, f"Beine Flachstahl {bb} × {b8}, Bohrung Ø 8,5 für Lagerbolzen M8", "tk")
    zeilen = [f"Drehachse Lehne: Bolzen M10 mit Gleitlagerbuchse, Achse {zahl(d['achse_z'] - d['deckel_z1'])} mm über Deckel, "
              f"{zahl(d['achse_x'])} mm ab linker Stirnseite.",
              f"Stützengelenk: {sb['stuetze_abstand']} mm hinter der Drehachse, {sb['stuetze_versatz']} mm unter der Lehnenplatte, Lagerböcke an den Eichenrippen.",
              "Unter dem Deckel je Gelenkplatte eine Gegenplatte Flachstahl 60 × 6 × 120 (nimmt Zugkräfte bei steiler Lehne auf)."]
    for i, z in enumerate(zeilen):
        bl.roh(f'<text class="t" x="40" y="{620 + i * 18}">{z}</text>')
    bl.speichern(ziel / "metallteile.svg")


def hantel(ziel, p, hs):
    h = p["hanteln"]
    x = hs[-1]
    s = 2.4
    bl = Blatt(1000, 470, "Kurzhantel – Aufbau", f"Maße in mm, gezeichnet: {zahl(x['kg'])} kg. Alle Gewichte siehe Tabelle in hanteln.md.")
    a = Ansicht(bl, 140, 260, s)
    R, lk, gl = x["D"] / 2, x["lk"], h["griff_laenge"]
    for u in (0, lk + gl):
        a.poly([(u + h["fase"], -R + h["abflachung"]), (u + lk - h["fase"], -R + h["abflachung"]),
                (u + lk, -R + h["abflachung"] + h["fase"]), (u + lk, R - h["fase"]), (u + lk - h["fase"], R),
                (u + h["fase"], R), (u, R - h["fase"]), (u, -R + h["abflachung"] + h["fase"])], "stahl")
        a.rect(u + (lk - h["gewinde_tiefe"] if u == 0 else 0), -h["kern_d"] / 2, h["gewinde_tiefe"], h["kern_d"], "d")
    a.rect(lk, -h["griff_d"] / 2, gl, h["griff_d"], "holz")
    a.linie(lk - h["gewinde_tiefe"], 0, lk + gl + h["gewinde_tiefe"], 0, "d")
    a.mass_h(0, lk, R, -20, ref=R)
    a.mass_h(lk, lk + gl, R, -20, ref=R)
    a.mass_h(lk + gl, 2 * lk + gl, R, -20, ref=R)
    a.mass_h(0, 2 * lk + gl, R, -44, ref=R)
    a.mass_v(-R, R, 2 * lk + gl, 30, f"Ø {x['D']}")
    a.mass_v(-R, -R + h["abflachung"], 0, -24, f"{h['abflachung']}", ref=0)
    a.mass_v(-h["griff_d"] / 2, h["griff_d"] / 2, lk + gl / 2, 0, f"Ø {h['griff_d']}")
    a.text(lk + gl / 2, -R - 18, "Eichengriff, Bohrung 16,5", "tk", "middle")
    a.text(lk / 2, -R - 18, f"Stahl S235, Fase {h['fase']}×45°", "tk", "middle")
    a.text(lk + gl / 2, R + 30, f"Gewindestange M16 8.8 × {x['kern_l']}, je {h['gewinde_tiefe']} tief eingeschraubt", "tk", "middle")
    bl.speichern(ziel / "hantel.svg")


def erzeuge(ziel, p, d, rs, park, hs):
    ziel.mkdir(parents=True, exist_ok=True)
    uebersicht(ziel, p, d)
    schnitt(ziel, p, d)
    rastleiste(ziel, p, d, rs, park)
    metall(ziel, p, d)
    hantel(ziel, p, hs)
