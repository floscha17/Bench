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
    k, po, me, ra = p["korpus"], p["polster"], p["mechanik"], p["rahmen"]
    se, sh, fh, fd = k["sockel_einzug"], k["sockel_hoehe"], k["fuss_h"], k["fuss_d"]
    lb, st = d["teile"]["lehne"], d["teile"]["sitz"]
    s = 0.72
    bl = Blatt(1100, 1380, "Übersicht – Hauptmaße", "Maße in mm. Polster flach, Rolltür geschlossen.")

    a = Ansicht(bl, 140, 480, s)
    bl.roh('<text class="ut" x="140" y="76">Vorderansicht (Raumseite)</text>')
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
        a.kreis(tl["achse_x"], d["achse_z"], 5, "stahl")
    a.rect(d["pedal_x"], fh + 14, 64, 6, "bronze")
    a.mass_h(0, L, H, -44, ref=H)
    kette = [0, d["lehne_x0"], d["lehne_x1"], d["sitz_x0"], d["sitz_x1"], L]
    for x0, x1 in zip(kette, kette[1:]):
        a.mass_h(x0, x1, H, -20, ref=H)
    a.mass_h(0, lb["achse_x"], 0, 26, f"Drehachse Lehne {zahl(lb['achse_x'])}", ref=d["achse_z"])
    a.mass_h(0, st["achse_x"], 0, 46, f"Drehachse Sitz {zahl(st['achse_x'])}", ref=d["achse_z"])
    a.mass_h(0, d["rt_x0"], 0, 66, ref=d["boden_z1"])
    a.mass_h(d["rt_x0"], d["rt_x1"], 0, 66, f"Rolltür {zahl(d['rt_len'])}", ref=d["boden_z1"])
    for z0, z1 in ((0, sh), (sh, d["rand_top"]), (d["rand_top"], H)):
        a.mass_v(z0, z1, L, 34)
    a.mass_v(0, H, L, 70)

    a = Ansicht(bl, 140, 930, s)
    bl.roh('<text class="ut" x="140" y="590">Draufsicht ohne Polster (Bettseite oben)</text>')
    a.rect(0, 0, L, D, "holz", R)
    a.rect(t, t, L - 2 * t, D - 2 * t, "innen", R - t)
    a.rect(d["lehne_x0"], d["pad_y0"], d["lehne_l"], d["pad_b"], "d", d["pad_r_aussen"])
    a.rect(d["sitz_x0"], d["pad_y0"], st["laenge"], d["pad_b"], "d", d["pad_r_aussen"])
    for y in d["rohr_y0"]:
        a.rect(t + 3, y, L - 2 * t - 6, ra["rohr_b"], "dunkel")
    for tl in (lb, st):
        for y in d["bein_y0"]:
            a.rect(tl["schiene_x0"], y + me["bein_breite"] / 2 - me["schiene_b"] / 2, tl["schiene_x1"] - tl["schiene_x0"], me["schiene_b"], "stahl")
    for x in d["mw_x"]:
        a.rect(x, d["fach_y0"], d["ti"], d["fach_tiefe"], "d")
    a.text(d["tasche_x1"] + 20, D / 2, "Gleitschienen Lehne (siehe gleitschienen.svg)", "tk")
    a.text(st["schiene_x0"], D / 2 + 30, "Gleitschienen Sitz", "tk")
    a.mass_v(0, D, L, 46)
    a.mass_v(0, d["pad_y0"], L, 16)
    a.mass_v(D - d["pad_y0"], D, L, 16)
    a.mass_v(0, d["rohr_y0"][0], 0, -16)
    a.mass_v(d["rohr_y0"][0], d["rohr_y0"][0] + ra["rohr_b"], 0, -16)
    kette = [0, d["tasche_x1"]] + d["mw_x"][1:] + [L - t, L]
    for x0, x1 in zip(kette, kette[1:]):
        a.mass_h(x0, x1, 0, 22)
    a.text(-40, 0, "vorne / Raum", "tk", "end", dy=4)
    a.text(-40, D, "hinten / Bett", "tk", "end", dy=4)
    a.text(L / 2, -60, f"Ecken R {R}, Rand {t} mm, Wanne {po['rand']} mm tief; dunkel: Längsrohre des Innenrahmens; gestrichelt: Trennwände", "tk", "middle")

    a = Ansicht(bl, 140, 1335, s)
    bl.roh('<text class="ut" x="140" y="996">Seitenansicht von rechts</text>')
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
    bl.speichern(ziel / "uebersicht.svg")


def schnitt(ziel, p, d, hs):
    D, H, t = d["D"], d["H"], d["t"]
    k, po, rt, me, ra = p["korpus"], p["polster"], p["rolltuer"], p["mechanik"], p["rahmen"]
    se, sh, fh, fd = k["sockel_einzug"], k["sockel_hoehe"], k["fuss_h"], k["fuss_d"]
    s = 1.5
    bl = Blatt(1220, 930, "Querschnitt durch den Hantelbereich",
               "Maße in mm. Schnitt quer zur Bank, links vorne (Raum), rechts hinten (Bett). Stahl dunkel, Holz hell.")
    a = Ansicht(bl, 400, 800, s)
    st = ra["stuetze"]
    for y in d["stuetze_y"]:
        a.rect(y + st / 2 - fd / 2, 0, fd, fh, "dunkel")
        a.rect(y, fh + 25, st, d["deckel_z1"] - fh - 25, "stahl")
    a.rect(d["stuetze_y"][0], d["deckel_z0"] - st, d["stuetze_y"][1] - d["stuetze_y"][0] + st, st, "stahl")
    a.rect(se, fh, 20, sh - fh, "holz")
    a.rect(D - se - 20, fh, 20, sh - fh, "holz")
    a.rect(t, sh, D - 2 * t, t, "holz")
    a.rect(t, d["deckel_z0"], D - 2 * t, t, "holz")
    a.rect(0, sh, t, t, "holz")
    a.rect(0, d["deckel_z0"], t, t + po["rand"], "holz")
    a.rect(D - t, sh, t, d["korpus_h"], "holz")
    for y in d["stuetze_y"]:  # Stützen laufen durch Boden und Wannenboden bis unter die Längsrohre
        a.rect(y, fh + 25, st, d["deckel_z1"] - fh - 25, "stahl")
    nut = rt["nut"]
    for y0 in (d["rt_y0"], d["rt_hinten_y0"]):
        a.rect(y0, d["boden_z1"] + 1, rt["lamelle_dicke"], d["innen_h"] - 2, "holz")
    for y in d["rohr_y0"]:
        a.rect(y, d["deckel_z1"], ra["rohr_b"], ra["rohr_h"], "stahl")
    for y in d["bein_y0"]:
        a.rect(y + me["bein_breite"] / 2 - me["schiene_b"] / 2, d["deckel_z1"], me["schiene_b"], me["schiene_h"], "stahl")
    for y in d["rippe_y0"]:
        a.rect(y, d["polster_z0"] - me["rippe_hoehe"], me["rippe_breite"], me["rippe_hoehe"], "holz")
    a.rect(d["pad_y0"], d["polster_z0"], d["pad_b"], po["platte"], "holz", 2)
    a.rect(d["pad_y0"], d["polster_z0"] + po["platte"], d["pad_b"], po["schaum"], "leder", 8)
    # Hantel in Aufnahme, untere Ebene
    x = hs[-1]
    ty = [d["fach_y0"] + d["fach_tiefe"] / 2 - p["hanteln"]["griff_laenge"] / 2 + 15,
          d["fach_y0"] + d["fach_tiefe"] / 2 + p["hanteln"]["griff_laenge"] / 2 - 15]
    for z in (d["boden_z1"], d["ebene_z0"]):
        for y in ty:
            a.rect(y - ra["traverse_t"] / 2, z, ra["traverse_t"], ra["traverse_b"], "stahl")
    y_h = d["fach_y0"] + (d["fach_tiefe"] - x["laenge"]) / 2
    zk = d["boden_z1"] + k["halter_luft"]
    for yy in (y_h, y_h + x["laenge"] - x["lk"]):
        a.rect(yy, zk, x["lk"], x["D"], "stahl", 3)
    zg = zk + x["D"] / 2 - p["hanteln"]["griff_d"] / 2
    a.rect(y_h + x["lk"], zg, x["laenge"] - 2 * x["lk"], p["hanteln"]["griff_d"], "holz")
    for y in ty:
        a.rect(y - 7, d["boden_z1"] + ra["traverse_b"], 14, zg - d["boden_z1"] - ra["traverse_b"], "leder")
    kette = [0, fh, sh, d["boden_z1"], d["ebene_z0"], d["deckel_z0"], d["deckel_z1"], d["polster_z0"], H]
    for z0, z1 in zip(kette, kette[1:]):
        a.mass_v(z0, z1, D, 40, ref=D)
    a.mass_v(0, H, D, 90, ref=D)
    kette = [0, d["rt_y0"], d["rt_y0"] + rt["lamelle_dicke"], d["fach_y0"], d["fach_y1"],
             d["rt_hinten_y0"] + rt["lamelle_dicke"], D - t, D]
    for y0, y1 in zip(kette, kette[1:]):
        a.mass_h(y0, y1, 0, 46, txt=f"Nutzraum {zahl(d['fach_tiefe'])}" if y0 == d["fach_y0"] else None)
    a.mass_h(0, D, 0, 74)
    a.mass_h(0, t, H, -24, ref=H)
    a.mass_h(t, d["pad_y0"], H, -24, ref=H)
    a.mass_h(d["pad_y0"], D - d["pad_y0"], H, -24, ref=H)
    notizen = [
        (H - po["schaum"] / 2, f"Leder + Schaum {po['schaum']}"),
        (d["polster_z0"] + po["platte"] / 2, f"Polsterplatte {po['platte']} mit Eichenkante"),
        (d["deckel_z1"] + po["rand"] / 2, f"Wanne {po['rand']}: Längsrohre {ra['rohr_b']}×{ra['rohr_h']}, Gleitschienen, Rippen"),
        (d["deckel_z0"] + t / 2, f"Wannenboden {t} furniert, Laufnuten {nut} × {nut}"),
        ((d["ebene_z1"] + d["deckel_z0"]) / 2, "obere Hantelebene (Traversen)"),
        ((d["boden_z1"] + d["ebene_z0"]) / 2, "untere Hantelebene: Hantel hängt am Griff"),
        (sh + t / 2, f"Boden {t} furniert"),
        ((fh + sh) / 2, f"Sockelzarge, {se} zurückgesetzt; Rollenrahmen innen"),
        (fh / 2, "Stellfüße an den Eckstützen"),
    ]
    for z, txt in notizen:
        a.text(-12, z, txt, "tk", "end", dy=4)
    bl.speichern(ziel / "schnitt.svg")


def gleitschienen(ziel, p, d, rast):
    me = p["mechanik"]
    bl = Blatt(1100, 760, "Gleitschienen mit Rastlöchern (je Klappteil 2 Stück)",
               "Maße in mm ab Drehachse. C-Profil auf den Querrohren, Indexbolzen Ø "
               f"{me['bolzen_d']} federnd. Flach: Gleitschuh am Endanschlag, Kugelschnäpper.")
    oy = 260
    for teil in ("lehne", "sitz"):
        tl = d["teile"][teil]
        rs, _ = rast[teil]
        u0, u1 = tl["u0"], tl["u1"]
        s = 1.0 if teil == "lehne" else 1.8
        # Lehne gespiegelt (Achse rechts), damit links wie an der Bank links ist
        m = (lambda u: u1 + u0 - u) if tl["dir"] < 0 else (lambda u: u)
        a = Ansicht(bl, (1000 - (u1 + u0) * s) if tl["dir"] < 0 else 120, oy, s)
        bl.roh(f'<text class="ut" x="40" y="{oy - 110}">{"Rückenlehne" if teil == "lehne" else "Sitz"} '
               f'(Achse bei x = {zahl(tl["achse_x"])} mm, Schiene x = {zahl(tl["schiene_x0"])}…{zahl(tl["schiene_x1"])} mm)</text>')
        a.rect(min(m(u0), m(u1)), 0, u1 - u0, me["schiene_h"], "stahl")
        a.linie(m(0), -30 / s, m(0), me["schiene_h"] + 50 / s, "d")
        a.text(m(0), me["schiene_h"] + 56 / s, "Achse", "tk", "middle")
        werte = sorted((r_ for r_ in rs if r_["ok"]), key=lambda r_: r_["n"])
        for i, r_ in enumerate(werte):
            n = r_["n"]
            if r_["winkel"] > 0:
                a.kreis(m(n), me["schiene_h"] / 2, me["bolzen_d"] / 2, "bg")
                lab = f"{r_['winkel']}°"
            else:
                a.rect(m(n) - 2, 0, 4, me["schiene_h"], "bronze")
                lab = "flach (Anschlag)"
            a.text(m(n), me["schiene_h"] + (12 + 14 * (i % 3)) / s, lab, "t", "middle")
            a.mass_h(m(n), m(0), 0, 24 + 16 * i, txt=zahl(round(n, 1)), ref=0)
        oy += 330
    bl.speichern(ziel / "gleitschienen.svg")


def metall(ziel, p, d, rast):
    me, ra, ro = p["mechanik"], p["rahmen"], p["rollen"]
    lb, st = d["teile"]["lehne"], d["teile"]["sitz"]
    bl = Blatt(1150, 690, "Metallbau – Prinzip und Entwurfsmaße",
               "Maße in mm. Stahl schwarz beschichtet. Auslegung, Profile und Verbindungen durch Metallbau bzw. Beschlaglieferant.")
    # Gelenkkonsole
    a = Ansicht(bl, 110, 300, 1.6)
    bl.roh('<text class="ut" x="40" y="90">Gelenkkonsole (2×, auf den Längsrohren)</text>')
    hz = d["achse_z"] - (d["deckel_z1"] + ra["rohr_h"])
    kb = me["konsole_breite"] / 2
    a.poly([(-kb, 0), (kb, 0), (kb, 6), (10, hz), (0, hz + 10), (-10, hz), (-kb, 6)], "stahl")
    a.kreis(0, hz, 5.25, "bg")
    a.mass_v(0, hz, kb, 30, ref=0)
    a.mass_h(-kb, kb, 0, 18)
    a.text(-30, -30, f"Dicke {me['gelenkplatte']}, Achse M10 gemeinsam für Lehne und Sitz,", "tk")
    a.text(-30, -40, "Laschen beider Polster mit Gleitlagern auf derselben Achse,", "tk")
    a.text(-30, -50, "auf das Längsrohr geschweißt, im Spalt neben dem Polster", "tk")
    # Gleitstütze
    a = Ansicht(bl, 470, 360, 0.55)
    bl.roh('<text class="ut" x="400" y="90">Gleitstütze Lehne / Sitz</text>')
    for i, tl in enumerate((lb, st)):
        x0 = i * 380
        for y in (0, d["stab_l"] - me["bein_breite"]):
            a.rect(x0 + y, 0, me["bein_breite"], tl["l"], "stahl")
            a.kreis(x0 + y + me["bein_breite"] / 2, tl["l"], 4.25, "bg")
            a.rect(x0 + y - 2, -12, me["bein_breite"] + 4, 12, "bronze")
        a.rect(x0, 20, d["stab_l"], 12, "stahl")
        a.mass_v(0, tl["l"], x0 + d["stab_l"], 20, f"{zahl(tl['l'])}", ref=x0 + d["stab_l"])
        a.text(x0 + d["stab_l"] / 2, tl["l"] + 30, "Rückenlehne" if tl["teil"] == "lehne" else "Sitz", "t", "middle")
    a.text(0, -40, f"Beine Flachstahl {me['bein_breite']} × {me['bein_dicke']}, Gleitschuhe (bronze) mit Indexbolzen Ø {me['bolzen_d']}", "tk")
    # Hantelaufnahme
    a = Ansicht(bl, 870, 300, 1.2)
    bl.roh('<text class="ut" x="850" y="90">Hantelaufnahme (je Hantel)</text>')
    a.rect(0, 0, 200, ra["traverse_b"], "stahl")
    for x in (40, 160):
        a.rect(x - 7, ra["traverse_b"], 14, 20, "stahl")
        a.rect(x - 9, ra["traverse_b"] + 20, 18, 4, "leder")
    a.rect(20, ra["traverse_b"] + 24, 160, p["hanteln"]["griff_d"], "holz")
    a.rect(-30, ra["traverse_b"] + 24 - 30, 50, 100, "stahl", 6)
    a.rect(180, ra["traverse_b"] + 24 - 30, 50, 100, "stahl", 6)
    a.poly([(28, ra["traverse_b"] + 24), (28, ra["traverse_b"] + 64), (52, ra["traverse_b"] + 64), (52, ra["traverse_b"] + 24),
            (48, ra["traverse_b"] + 24), (48, ra["traverse_b"] + 60), (32, ra["traverse_b"] + 60), (32, ra["traverse_b"] + 24)], "dunkel")
    a.text(100, -20, "2 gepolsterte Auflagen am Griff, Griffmitte frei,", "tk", "middle")
    a.text(100, -30, "Sicherungsbügel an einer Griffschulter, Traverse hochkant", "tk", "middle")
    # Fahrwerk
    a = Ansicht(bl, 110, 560, 0.6)
    bl.roh('<text class="ut" x="40" y="450">Fahrwerk (Prinzip)</text>')
    x0 = d["rollen_pos"][0][0]
    x1 = d["rollen_pos"][1][0]
    a.rect(x0 - 20, 60, x1 - x0 + 40, 10, "stahl")
    for x in (x0, x1):
        a.kreis(x, ro["durchmesser"] / 2 + 4, ro["durchmesser"] / 2, "stahl")
        a.rect(x - 5, ro["durchmesser"] + 4, 10, 56 - ro["durchmesser"], "stahl")
    for x in (x0 + 50, x1 - 50):
        a.kreis(x, 80, 8, "dunkel")
    a.linie(x0 + 50, 80, x1 - 50, 80, "k")
    a.rect(d["pedal_x"] - 20, 20, 64, 6, "bronze")
    for x in (d["fuss_pos"][0][0], d["fuss_pos"][1][0]):
        a.rect(x - 20, 0, 40, 10, "dunkel")
    a.linie(-20, 0, d["L"] + 20, 0, "k")
    a.text(0, -30, f"Pedal rechts → 2 gekoppelte Exzenterwellen → geführter Rollenrahmen mit {ro['anzahl']} Lenkrollen Ø {ro['durchmesser']}; "
                   f"Hub {ro['hub']} mm, Totpunktrast in beiden Lagen. Option: Spindelantrieb mit Taster.", "tk")
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
    for alt in ("rastleiste.svg",):
        (ziel / alt).unlink(missing_ok=True)
    uebersicht(ziel, p, d)
    schnitt(ziel, p, d, hs)
    gleitschienen(ziel, p, d, rast)
    metall(ziel, p, d, rast)
    hantel(ziel, p, hs)
