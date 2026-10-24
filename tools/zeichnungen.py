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
  .fl { stroke: #9b7b55; stroke-width: 0.6; }
  .bronze { fill: #a07a45; stroke: #1d1d1b; stroke-width: 1; }
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

    def rect(self, u, v, w, h, cls="k", r=0):
        x, y = self.p(u, v + h)
        self.bl.roh(f'<rect class="{cls}" x="{x:.1f}" y="{y:.1f}" width="{w * self.s:.1f}" height="{h * self.s:.1f}" '
                    f'rx="{r * self.s:.1f}"/>')

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
    L, D, H, t, R = d["L"], d["D"], d["H"], d["t"], d["R"]
    k, po = p["korpus"], p["polster"]
    se, sh, fh, fd = k["sockel_einzug"], k["sockel_hoehe"], k["fuss_h"], k["fuss_d"]
    lb, st = d["teile"]["lehne"], d["teile"]["sitz"]
    s = 0.62
    bl = Blatt(1100, 1330, "Übersicht – Hauptmaße", "Maße in mm. Polster flach, Rolltür geschlossen.")

    # Vorderansicht
    a = Ansicht(bl, 140, 450, s)
    bl.roh('<text class="ut" x="140" y="90">Vorderansicht (Raumseite)</text>')
    for x, _ in d["fuss_pos"][:2]:
        a.rect(x - fd / 2, 0, fd, fh, "dunkel")
    a.rect(se, fh, L - 2 * se, sh - fh, "holz", 4)
    a.rect(0, sh, L, d["korpus_h"], "holz", 8)
    for x in (R, L - R):
        a.linie(x, sh, x, d["rand_top"], "d")
    a.rect(d["rt_x0"], d["boden_z1"], d["rt_len"], d["innen_h"], "innen")
    schritt = d["rt_b"] + p["rolltuer"]["lamelle_fuge"]
    for i in range(1, d["rt_n"]):
        x = d["rt_x0"] + i * schritt
        a.linie(x, d["boden_z1"], x, d["deckel_z0"], "fl")
    for x0, x1 in ((d["lehne_x0"], d["lehne_x1"]), (d["sitz_x0"], d["sitz_x1"])):
        a.rect(x0, d["polster_z0"], x1 - x0, po["platte"], "holz", 3)
        a.rect(x0, d["polster_z0"] + po["platte"], x1 - x0, po["schaum"], "leder", 10)
    for tl in (lb, st):
        a.kreis(tl["achse_x"], d["achse_z"], 6, "stahl")
    a.rect(d["pedal_x"], 16, 64, 6, "bronze")
    a.mass_h(0, L, H, -44, ref=H)
    kette = [0, d["lehne_x0"], d["lehne_x1"], d["sitz_x0"], d["sitz_x1"], L]
    for x0, x1 in zip(kette, kette[1:]):
        a.mass_h(x0, x1, H, -20, ref=H)
    a.mass_h(0, lb["achse_x"], 0, 26, f"Drehachse Lehne {zahl(lb['achse_x'])}", ref=d["achse_z"])
    a.mass_h(0, st["achse_x"], 0, 46, f"Drehachse Sitz {zahl(st['achse_x'])}", ref=d["achse_z"])
    a.mass_h(0, d["rt_x0"], 0, 66, ref=d["boden_z1"])
    a.mass_h(d["rt_x0"], d["rt_x1"], 0, 66, f"Rolltür {zahl(d['rt_len'])}", ref=d["boden_z1"])
    a.mass_h(d["pedal_x"], d["pedal_x"] + 64, 0, 26, "Fußhebel")
    for z0, z1 in ((0, fh), (fh, sh), (sh, d["rand_top"]), (d["rand_top"], H)):
        a.mass_v(z0, z1, L, 34)
    a.mass_v(0, H, L, 70)

    # Draufsicht ohne Polster
    a = Ansicht(bl, 140, 900, s)
    bl.roh('<text class="ut" x="140" y="560">Draufsicht ohne Polster (Bettseite oben)</text>')
    a.rect(0, 0, L, D, "holz", R)
    a.rect(t, t, L - 2 * t, D - 2 * t, "innen", R - t)
    a.rect(d["lehne_x0"], d["pad_y0"], d["lehne_l"], d["pad_b"], "d", d["pad_r_aussen"])
    a.rect(d["sitz_x0"], d["pad_y0"], st["laenge"], d["pad_b"], "d", d["pad_r_aussen"])
    for tl in (lb, st):
        for y in d["leiste_y0"]:
            a.rect(tl["leiste_x0"], y, tl["leiste_x1"] - tl["leiste_x0"], p["mechanik"]["leiste_breite"], "dunkel")
    for y in (t + 0.5, D - t - 5.5):
        a.rect(lb["achse_x"] - 14, y, st["achse_x"] - lb["achse_x"] + 28, 5, "stahl")
    for x in d["mw_x"]:
        a.rect(x, d["fach_y0"], d["ti"], d["fach_tiefe"], "d")
    a.text(d["tasche_x0"] + 6, d["fach_y0"] + 20, "Tasche", "tk")
    a.text(lb["leiste_x0"] + 10, D / 2, "Rastleisten Lehne (siehe rastleiste.svg)", "tk")
    a.text(st["leiste_x0"] + 10, D / 2, "Auflageleisten Sitz", "tk")
    a.mass_v(0, D, L, 46)
    a.mass_v(0, d["pad_y0"], L, 16)
    a.mass_v(D - d["pad_y0"], D, L, 16)
    a.mass_v(0, d["leiste_y0"][0], 0, -16)
    a.mass_v(d["leiste_y0"][1] + p["mechanik"]["leiste_breite"], D, 0, -16)
    kette = [0, d["tasche_x1"]] + [x for x in d["mw_x"][1:]] + [L - t, L]
    for x0, x1 in zip(kette, kette[1:]):
        a.mass_h(x0, x1, 0, 22)
    a.text(-40, 0, "vorne / Raum", "tk", "end", dy=4)
    a.text(-40, D, "hinten / Bett", "tk", "end", dy=4)
    a.text(L / 2, -60, f"Ecken R {R}, Rand {t} mm breit, Wanne {po['rand']} mm tief, Trennwände gestrichelt", "tk", "middle")

    # Seitenansicht
    a = Ansicht(bl, 140, 1280, s)
    bl.roh('<text class="ut" x="140" y="960">Seitenansicht von rechts</text>')
    for y in (d["fuss_pos"][0][1], d["fuss_pos"][2][1]):
        a.rect(y - fd / 2, 0, fd, fh, "dunkel")
    a.rect(se, fh, D - 2 * se, sh - fh, "holz", 4)
    a.rect(0, sh, D, d["korpus_h"], "holz", 8)
    for y in (R, D - R):
        a.linie(y, sh, y, d["rand_top"], "d")
    a.rect(d["pad_y0"], d["polster_z0"], d["pad_b"], po["platte"], "holz", 3)
    a.rect(d["pad_y0"], d["polster_z0"] + po["platte"], d["pad_b"], po["schaum"], "leder", 10)
    a.mass_h(0, D, 0, 20)
    a.mass_v(0, H, D, 30)
    a.text(D + 70, 30, "Absenkrollen verdeckt in der Sockelzarge", "tk")
    bl.speichern(ziel / "uebersicht.svg")


def schnitt(ziel, p, d, hs):
    D, H, t = d["D"], d["H"], d["t"]
    k, po, rt, me = p["korpus"], p["polster"], p["rolltuer"], p["mechanik"]
    se, sh, fh, fd = k["sockel_einzug"], k["sockel_hoehe"], k["fuss_h"], k["fuss_d"]
    s = 1.5
    bl = Blatt(1220, 930, "Querschnitt durch ein Hantelfach",
               "Maße in mm. Schnitt quer zur Bank unter der Rückenlehne, links vorne (Raum), rechts hinten (Bett).")
    a = Ansicht(bl, 400, 800, s)
    for y in (d["fuss_pos"][0][1], d["fuss_pos"][2][1]):
        a.rect(y - fd / 2, 0, fd, fh, "dunkel")
    a.rect(se, fh, 20, sh - fh, "holz")
    a.rect(D - se - 20, fh, 20, sh - fh, "holz")
    a.rect(t, sh, D - 2 * t, t, "holz")                                   # Boden
    a.rect(t, d["deckel_z0"], D - 2 * t, t, "holz")                       # Deckel
    a.rect(0, sh, t, t, "holz")                                           # Frontleiste unten
    a.rect(0, d["deckel_z0"], t, t + po["rand"], "holz")                  # Frontleiste oben mit Rand
    a.rect(D - t, sh, t, d["korpus_h"], "holz")                           # Rückwand
    nut = rt["nut"]
    for y0 in (d["rt_y0"], d["rt_hinten_y0"]):
        a.rect(y0, d["boden_z1"] + 1, rt["lamelle_dicke"], d["innen_h"] - 2, "holz")
        yz = y0 + (rt["lamelle_dicke"] - nut) / 2
        a.rect(yz, d["boden_z1"] - nut, nut, nut, "k")
        a.rect(yz, d["deckel_z0"], nut, nut, "k")
    if k["fachboden"]:
        a.rect(d["fach_y0"] + 5, d["fachboden_z0"], d["fach_tiefe"] - 5, d["ti"], "innen")
    x = hs[-1]
    y_h = d["fach_y0"] + (d["fach_tiefe"] - x["laenge"]) / 2
    for yy in (y_h, y_h + x["laenge"] - x["lk"]):
        a.rect(yy, d["boden_z1"], x["lk"], k["ablage_h"], "dunkel")
        a.rect(yy, d["boden_z1"] + k["ablage_h"], x["lk"], x["liegehoehe"], "stahl", 3)
    a.rect(y_h + x["lk"], d["boden_z1"] + k["ablage_h"] + x["liegehoehe"] / 2 - p["hanteln"]["griff_d"] / 2,
           x["laenge"] - 2 * x["lk"], p["hanteln"]["griff_d"], "holz")
    for y in d["leiste_y0"]:
        a.rect(y, d["deckel_z1"], me["leiste_breite"], po["rand"], "dunkel")
    for y in d["rippe_y0"]:
        a.rect(y, d["polster_z0"] - me["rippe_hoehe"], me["rippe_breite"], me["rippe_hoehe"], "holz")
    a.rect(d["pad_y0"], d["polster_z0"], d["pad_b"], po["platte"], "holz", 2)
    a.rect(d["pad_y0"], d["polster_z0"] + po["platte"], d["pad_b"], po["schaum"], "leder", 8)
    kette = [0, fh, sh, d["boden_z1"]]
    if k["fachboden"]:
        kette += [d["fachboden_z0"], d["fachboden_z1"]]
    kette += [d["deckel_z0"], d["deckel_z1"], d["polster_z0"], d["polster_z0"] + po["platte"], H]
    for z0, z1 in zip(kette, kette[1:]):
        a.mass_v(z0, z1, D, 40, ref=D)
    a.mass_v(0, H, D, 90, ref=D)
    kette = [0, d["rt_y0"], d["rt_y0"] + rt["lamelle_dicke"], d["fach_y0"], d["fach_y1"],
             d["rt_hinten_y0"] + rt["lamelle_dicke"], D - t, D]
    for y0, y1 in zip(kette, kette[1:]):
        a.mass_h(y0, y1, 0, 46, txt=f"Fachtiefe {zahl(d['fach_tiefe'])}" if y0 == d["fach_y0"] else None)
    a.mass_h(0, D, 0, 74)
    a.mass_h(0, se, 0, 22)
    a.mass_h(D - se, D, 0, 22)
    a.mass_h(0, t, H, -24, ref=H)
    a.mass_h(t, d["pad_y0"], H, -24, ref=H)
    a.mass_h(d["pad_y0"], D - d["pad_y0"], H, -24, ref=H)
    notizen = [
        (H - po["schaum"] / 2, "Leder + Schaum 30 hart / 20 mittel"),
        (d["polster_z0"] + po["platte"] / 2, f"Polsterplatte {po['platte']} mit Eichenkante"),
        (d["deckel_z1"] + po["rand"] / 2, f"Wanne {po['rand']} tief: Rastleisten, Rippen, Gelenkplatten"),
        (d["deckel_z0"] + t / 2, f"Deckel Eiche massiv {t}, Laufnuten {nut} × {nut}"),
        ((d["fachboden_z1"] + d["deckel_z0"]) / 2 if k["fachboden"] else d["deckel_z0"] - 40, "obere Ebene"),
        ((d["boden_z1"] + (d["fachboden_z0"] or d["deckel_z0"])) / 2, f"untere Ebene {k['fach_unten']}: Hanteln auf Ablage"),
        (sh + t / 2, f"Boden Eiche massiv {t}, Laufnuten"),
        ((fh + sh) / 2, f"Sockelzarge Eiche, {se} zurückgesetzt"),
        (fh / 2, "Füße schwarz"),
    ]
    for z, txt in notizen:
        a.text(-12, z, txt, "tk", "end", dy=4)
    zt = (d["fachboden_z1"] or d["boden_z1"]) + 30
    a.text(d["rt_y0"] + 20, zt, "← Rolltür vorn (geschlossen)", "tk")
    a.text(d["rt_hinten_y0"] - 4, zt, "Rolltür hinten (offen) →", "tk", "end")
    bl.speichern(ziel / "schnitt.svg")


def rastleiste(ziel, p, d, rs, park):
    me, po = p["mechanik"], p["polster"]
    tl = d["teile"]["lehne"]
    hoehe, r = po["rand"], me["buegel_d"] / 2
    s = 1.0
    bl = Blatt(1100, 620, "Rastleiste der Rückenlehne (2 Stück, spiegelgleich)",
               "Maße in mm ab Drehachse der Lehne, gemessen nach links. Eiche massiv, schwarz gebeizt, mit dem Deckel verleimt und verschraubt.")
    u0, u1 = tl["u0"], tl["u1"]
    a = Ansicht(bl, 1060 - u1 * s, 300, s)
    # gespiegelt zeichnen, damit links wie an der Bank links ist: u wächst nach links
    def m(u):
        return u1 - u
    a.rect(m(u1), 0, u1 - u0, hoehe, "dunkel")
    a.linie(m(0), -30, m(0), hoehe + 60, "d")
    a.text(m(0), hoehe + 66, "Drehachse", "tk", "middle")
    marken = [(r_["n"], f"{r_['winkel']}°", me["rast_tiefe"]) for r_ in rs if r_["ok"]] + [(park, "Park 0°", d["park_tiefe"])]
    marken.sort()
    for i, (n, lab, tiefe) in enumerate(marken):
        a.rect(m(n) - r - 0.5, hoehe - tiefe, 2 * r + 1, tiefe, "bg")
        a.kreis(m(n), hoehe - tiefe + r, r, "stahl")
        a.text(m(n), hoehe + (12 if i % 2 == 0 else 28), lab, "t", "middle")
        a.mass_h(m(n), m(0), 0, 28 + 18 * i, txt=zahl(round(n, 1)), ref=hoehe - tiefe)
    a.mass_v(0, hoehe, m(u0), 24)
    a.mass_h(m(u0), m(0), hoehe, -30, ref=hoehe)
    a.mass_h(m(u1), m(u0), hoehe, -70, f"Leiste {zahl(u1 - u0)}", ref=hoehe)
    zeilen = [f"Rasten: Ø {me['buegel_d'] + 1} halbrund, {me['rast_tiefe']} tief. Parkrast {zahl(d['park_tiefe'])} tief, nach oben offen.",
              f"Lage quer: {zahl(d['leiste_y0'][0])} mm ab Vorderkante bzw. {zahl(d['D'] - d['leiste_y0'][1] - me['leiste_breite'])} mm ab Hinterkante, Breite {me['leiste_breite']}.",
              f"Drehachse der Lehne: {zahl(tl['achse_x'])} mm ab linker Stirnseite, {zahl(d['achse_z'] - d['deckel_z1'])} mm über dem Deckel.",
              f"Leiste von x = {zahl(tl['leiste_x0'])} bis {zahl(tl['leiste_x1'])} mm ab linker Stirnseite.",
              "Beide Leisten gemeinsam bearbeiten (zusammengespannt), damit die Rasten exakt fluchten."]
    for i, z in enumerate(zeilen):
        bl.roh(f'<text class="t" x="40" y="{500 + i * 18}">{z}</text>')
    bl.speichern(ziel / "rastleiste.svg")


def metall(ziel, p, d, stufen, gelenk):
    me = p["mechanik"]
    lb, st = d["teile"]["lehne"], d["teile"]["sitz"]
    s = 1.6
    bl = Blatt(1150, 760, "Metallteile – Entwurfsmaße für den Metallbau",
               "Maße in mm. Stahl S235, schwarz pulverbeschichtet. Fertigungszeichnung durch den Metallbau nach Aufmaß am Korpus.")
    # Gelenkplatte Korpus mit zwei Achsen
    a = Ansicht(bl, 120, 330, s)
    bl.roh('<text class="ut" x="40" y="90">Gelenkplatte Korpus (2×)</text>')
    hz = d["achse_z"] - d["deckel_z1"]
    ab = st["achse_x"] - lb["achse_x"]
    a.poly([(-14, 0), (ab + 14, 0), (ab + 14, 6), (ab + 11, hz), (ab, hz + 11), (0, hz + 11), (-11, hz), (-14, 6)], "stahl")
    for x in (0, ab):
        a.kreis(x, hz, 5.25, "bg")
    a.mass_v(0, hz, ab + 14, 40, ref=0)
    a.mass_h(0, ab, hz, -40, ref=hz)
    a.text(-14, -40, f"Dicke {me['gelenkplatte']}, Bohrungen Ø 10,5 (Bolzen M10)", "tk")
    a.text(-14, -50, "Fuß 90 mm nach innen gekantet, 4 × M6 durch Deckel", "tk")
    a.text(-14, -60, "auf Gegenplatte 140 × 60 × 6 unter dem Deckel", "tk")
    # Gelenkplatte Lehne/Sitz
    a = Ansicht(bl, 400, 330, s)
    bl.roh('<text class="ut" x="330" y="90">Gelenkplatte Lehne / Sitz (4×)</text>')
    hb = d["achse_z"] - d["polster_z0"]
    a.poly([(0, hb + 11), (-11, hb), (12, 0), (57, 0), (57, 4), (11, hb + 6)], "stahl")
    a.kreis(0, hb, 5.25, "bg")
    a.mass_v(0, hb, 57, 30, ref=0)
    a.mass_h(0, 57, 0, 20)
    a.text(-11, -40, "Lasche unter die Polsterplatte gekantet,", "tk")
    a.text(-11, -50, "3 × Senkschraube in Einschlagmuttern", "tk")
    # Klappbügel Sitz (seitlich gesehen, aufgeklappt)
    a = Ansicht(bl, 640, 330, 1.3)
    bl.roh('<text class="ut" x="610" y="90">Klappbügel Sitz (je Stellung 1×)</text>')
    for i, st_ in enumerate(stufen):
        x0 = i * 70
        a.rect(x0, 0, 8, st_["h"], "stahl")
        a.rect(x0 - 4, st_["h"] - 8, 16, 8, "stahl")
        a.kreis(x0 + 8, 4, 3, "bg")
        a.mass_v(0, st_["h"], x0 + 8, 18, f"{zahl(round(st_['h']))}", ref=x0 + 8)
        a.text(x0 + 4, -16, f"{st_['winkel']}°", "t", "middle")
        a.text(x0 + 4, -28, f"bei {zahl(st_['u'])}", "tk", "middle")
    a.text(-10, -50, "U-Bügel Flachstahl 30 × 8, Steg oben gummiert,", "tk")
    a.text(-10, -60, "Scharnier auf dem Deckel, Höhe ab Deckel;", "tk")
    a.text(-10, -70, "Breiten ineinander geschachtelt (je 24 mm schmaler)", "tk")
    # Klappstütze Lehne
    a = Ansicht(bl, 930, 640, 0.5)
    bl.roh('<text class="ut" x="900" y="90">Klappstütze Lehne (1×)</text>')
    l, bb, b8 = lb["l"], me["bein_breite"], me["bein_dicke"]
    y0, y1 = d["bein_y0"][0] - d["stab_y0"], d["bein_y0"][1] - d["stab_y0"]
    for y in (y0, y1):
        a.rect(y, 0, bb, l, "stahl")
        a.kreis(y + bb / 2, l, 4.25, "bg")
    a.rect(0, -me["buegel_d"] / 2, d["stab_l"], me["buegel_d"], "stahl")
    a.mass_v(0, l, y1 + bb, 26, f"{zahl(l)} Bohrung–Stabmitte", ref=y1 + bb / 2)
    a.mass_h(0, d["stab_l"], 0, 26, f"Querstab Ø {me['buegel_d']} × {zahl(d['stab_l'])}")
    a.text(0, -110, f"Beine Flachstahl {bb} × {b8}", "tk")
    zeilen = [f"Drehachsen: Lehne bei x = {zahl(lb['achse_x'])}, Sitz bei x = {zahl(st['achse_x'])} mm ab linker Stirnseite, "
              f"{zahl(hz)} mm über dem Deckel. Bolzen M10 mit Gleitlagerbuchse.",
              f"Stützengelenk Lehne: {lb['s']} mm von der Achse, {me['stuetze_versatz']} mm unter der Lehnenplatte, Lagerböcke an den Eichenrippen.",
              f"Absenkrollen: 4 lenkbare Doppelrollen Ø {p['rollen']['durchmesser']} auf Hubplatten, Exzenterwelle längs im Sockel, "
              f"Hub {p['rollen']['hub']} mm, Bronze-Fußhebel vorn rechts mit Totpunktrast in beiden Lagen.",
              "Alternative zur Eigenkonstruktion: fertiges Hubrollen-System (wie bei Werkbänken), verdeckt in die Sockelzarge eingebaut."]
    for i, z in enumerate(zeilen):
        bl.roh(f'<text class="t" x="40" y="{680 + i * 18}">{z}</text>')
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


def erzeuge(ziel, p, d, rast, hs):
    ziel.mkdir(parents=True, exist_ok=True)
    rs, park, _ = rast["lehne"]
    stufen, gelenk, _, _ = rast["sitz"]
    uebersicht(ziel, p, d)
    schnitt(ziel, p, d, hs)
    rastleiste(ziel, p, d, rs, park)
    metall(ziel, p, d, stufen, gelenk)
    hantel(ziel, p, hs)
