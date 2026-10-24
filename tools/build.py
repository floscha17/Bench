#!/usr/bin/env python3
"""Erzeugt aus params.toml alle abgeleiteten Dateien der Bank.

- cad/params.scad       Parameter + abgeleitete Maße für das OpenSCAD-Modell
- docs/stueckliste.md   Zuschnittliste, Metallteile, Beschläge, Gewicht, grobe Kosten
- docs/berechnung.md    Rasten von Lehne und Sitz, Stauraum, Durchbiegung, Kippsicherheit, Rollen
- docs/hanteln.md       Selbstbau-Hanteln: Maße je Gewicht, Fertigung, Kosten
- docs/zeichnungen/     Maßskizzen als SVG
- renders/*.png         Ansichten (nur wenn OpenSCAD installiert ist)

Aufruf:  python3 tools/build.py [--no-render] [--stuetze-suchen]
"""

import math
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

import zeichnungen

ROOT = Path(__file__).resolve().parent.parent
G = 9.81
E_STAHL = 210000
TEILE = ("lehne", "sitz")
NAME = {"lehne": "Rückenlehne", "sitz": "Sitz"}


def load_params():
    with open(ROOT / "params.toml", "rb") as f:
        return tomllib.load(f)


def rr_flaeche(l, b, r):
    """Fläche eines Rechtecks mit gerundeten Ecken."""
    return l * b - (4 - math.pi) * r * r


def rr_umfang(l, b, r):
    return 2 * (l + b) - (8 - 2 * math.pi) * r


def derive(p):
    """Alle abgeleiteten Maße an einer Stelle – SCAD, Doku und Zeichnungen nutzen dieselben Werte."""
    b, m, po, me, k, rt = (p["bank"], p["material"], p["polster"], p["mechanik"],
                           p["korpus"], p["rolltuer"])
    L, D, H, R = b["laenge"], b["tiefe"], b["hoehe"], b["eckradius"]
    t, ti = m["aussen"], m["innen"]
    d = {"L": L, "D": D, "H": H, "R": R, "t": t, "ti": ti}

    # Höhenaufbau: Polster → Rand (Wanne) → Deckel → Fächer → Boden → Sockel
    P = po["platte"] + po["schaum"]
    d["polster_h"] = P
    d["polster_z0"] = H - P
    d["rand_top"] = d["polster_z0"]
    d["deckel_z1"] = d["polster_z0"] - po["rand"]
    d["deckel_z0"] = d["deckel_z1"] - t
    d["boden_z0"] = k["sockel_hoehe"]
    d["boden_z1"] = d["boden_z0"] + t
    d["korpus_h"] = d["rand_top"] - d["boden_z0"]
    d["innen_l"] = L - 2 * t
    d["innen_h"] = d["deckel_z0"] - d["boden_z1"]

    # Polster in der Wanne: Lehne links, Fuge, Sitz rechts
    e = t + po["luft"]
    d["pad_y0"], d["pad_b"] = e, D - 2 * e
    d["pad_r_aussen"] = max(po["radius"], R - e)          # konzentrisch zur Korpusecke
    d["lehne_x0"] = e
    d["sitz_x1"] = L - e
    d["sitz_x0"] = d["sitz_x1"] - po["sitz_laenge"]
    d["lehne_x1"] = d["sitz_x0"] - po["fuge"]
    d["lehne_l"] = d["lehne_x1"] - d["lehne_x0"]

    # Rolltür vorn zwischen den Eckrundungen; offen läuft sie in die Tasche links und an der Rückseite entlang
    d["rt_x0"], d["rt_x1"] = R, L - R
    d["rt_len"] = d["rt_x1"] - d["rt_x0"]
    d["rt_y0"] = rt["luft"]
    n = round((d["rt_len"] + rt["lamelle_fuge"]) / (rt["lamelle_breite"] + rt["lamelle_fuge"]))
    d["rt_n"] = n
    d["rt_b"] = (d["rt_len"] - (n - 1) * rt["lamelle_fuge"]) / n
    d["rt_lamelle_l"] = d["innen_h"] + 2 * rt["nut"] - 2
    d["fach_y0"] = t + 2
    d["rt_hinten_y0"] = D - t - rt["luft"] - rt["lamelle_dicke"]
    d["fach_y1"] = d["rt_hinten_y0"] - 3
    d["fach_tiefe"] = d["fach_y1"] - d["fach_y0"]
    d["rt_speicher"] = d["fach_tiefe"] + (d["innen_l"] - k["tasche"]) - 2 * rt["biegeradius"]

    # Tasche, Trennwände, Fächer
    d["tasche_x0"], d["tasche_x1"] = t, t + k["tasche"]
    breiten = list(k["faecher"])
    rest = d["innen_l"] - k["tasche"] - ti - sum(breiten) - len(breiten) * ti
    breiten.append(rest)
    d["fach_breiten"] = breiten
    x = d["tasche_x1"]
    d["mw_x"] = []
    d["fach_x0"] = []
    for i, bb in enumerate(breiten):
        d["mw_x"].append(x)
        x += ti
        d["fach_x0"].append(x)
        x += bb
    d["n_fach"] = len(breiten)
    d["n_mw"] = len(d["mw_x"])
    if k["fachboden"]:
        d["fachboden_z0"] = d["boden_z1"] + k["fach_unten"]
        d["fachboden_z1"] = d["fachboden_z0"] + ti
    else:
        d["fachboden_z0"] = d["fachboden_z1"] = None
    zellen = []
    for i, (x0, bb) in enumerate(zip(d["fach_x0"], breiten)):
        ebenen = ([("unten", d["boden_z1"], d["fachboden_z0"]), ("oben", d["fachboden_z1"], d["deckel_z0"])]
                  if k["fachboden"] else [("", d["boden_z1"], d["deckel_z0"])])
        # Zugang nur, soweit das Fach vor der Rolltüröffnung liegt
        offen = min(x0 + bb, d["rt_x1"]) - max(x0, d["rt_x0"])
        for ebene, z0, z1 in ebenen:
            zellen.append({"name": f"Fach {i + 1} {ebene}".strip(), "fach": i, "ebene": ebene,
                           "x0": x0, "z0": z0, "h": z1 - z0, "zugang": z1 - z0,
                           "breite": bb, "offen": offen, "tiefe": d["fach_tiefe"]})
    zellen.sort(key=lambda z: (z["ebene"] == "oben", z["fach"]))
    d["zellen"] = zellen

    # Sockel: Eichenzarge, Füße, Absenkrollen, Fußhebel
    se, fe = k["sockel_einzug"], k["fuss_einzug"]
    d["fuss_pos"] = [[fe, fe], [L - fe, fe], [fe, D - fe], [L - fe, D - fe]]
    rx = fe + 90
    d["rollen_pos"] = [[rx, fe], [L - rx, fe], [rx, D - fe], [L - rx, D - fe]]
    d["pedal_x"] = L - 170

    # Mechanik: gemeinsame Werte
    d["achse_z"] = H - me["achse_unter_oberkante"]
    d["vA"] = -(P - me["achse_unter_oberkante"]) - me["stuetze_versatz"]
    rr = me["buegel_d"] / 2
    d["rast_z"] = d["polster_z0"] - me["rast_tiefe"] + rr - d["achse_z"]
    d["park_tiefe"] = d["polster_z0"] - (d["achse_z"] + d["vA"]) + rr
    lb, le = me["leiste_breite"], me["leiste_einzug"]
    d["leiste_y0"] = [e + le, D - e - le - lb]
    d["bein_y0"] = [d["leiste_y0"][0] + lb + 2, d["leiste_y0"][1] - 2 - me["bein_breite"]]
    d["stab_y0"] = d["leiste_y0"][0] + 5
    d["stab_l"] = d["leiste_y0"][1] + lb - 5 - d["stab_y0"]
    rippe_y = d["bein_y0"][0] + me["bein_breite"] + 25
    d["rippe_y0"] = [rippe_y, D - rippe_y - me["rippe_breite"]]

    # Klappteile: Lehne dreht um ihre rechte Kante und hebt sich links, Sitz dreht um seine linke Kante
    d["teile"] = {}
    for teil, achse, richtung, laenge in (("lehne", d["lehne_x1"], -1, d["lehne_l"]),
                                          ("sitz", d["sitz_x0"], 1, po["sitz_laenge"])):
        q = p[teil]
        tl = {"teil": teil, "achse_x": achse, "dir": richtung, "laenge": laenge, "winkel": q["winkel"],
              "s": q.get("stuetze_abstand", q.get("bock_abstand")), "l": q.get("stuetze_laenge", 0),
              "u0": 40, "u1": laenge - 10}
        xa, xb = achse + richtung * tl["u0"], achse + richtung * tl["u1"]
        tl["leiste_x0"], tl["leiste_x1"] = min(xa, xb), max(xa, xb)
        tl["rippe_l"] = tl["s"] + tl["l"] - 45 if teil == "lehne" else 0
        d["teile"][teil] = tl
    return d


def gx(tl, u):
    """Lokale Lage auf einem Klappteil (ab Drehachse) → x ab linkem Ende."""
    return tl["achse_x"] + tl["dir"] * u


def rasten(p, d, teil, s=None, l=None):
    """Raststellungen der Stütze: Position je Winkel, Stützkraft, Achskraft."""
    tl, q, me, last = d["teile"][teil], p[teil], p["mechanik"], p["last"]
    s = s or tl["s"]
    l = l or tl["l"]
    vA, zN = d["vA"], d["rast_z"]
    F_last = q["last_anteil"] * last["nutzer_kg"] * G * last["dynamik"]
    out = []
    for a in tl["winkel"]:
        r = math.radians(a)
        Ax = s * math.cos(r) - vA * math.sin(r)
        Az = s * math.sin(r) + vA * math.cos(r)
        dz = Az - zN
        if dz >= l:
            out.append({"winkel": a, "ok": False})
            continue
        n = Ax + math.sqrt(l * l - dz * dz)
        ux, uz = (Ax - n) / l, dz / l             # Richtung Rast → Gelenk (Druckstab)
        hebel = Ax * uz - Az * ux
        # Lastfall 1: Gewicht senkrecht nach unten; Lastfall 2: Last senkrecht auf die Polsterfläche.
        lastfaelle = [
            ((0.0, -F_last), F_last * (q["last_abstand"] * math.cos(r) - me["achse_unter_oberkante"] * math.sin(r))),
            ((F_last * math.sin(r), -F_last * math.cos(r)), F_last * q["last_abstand"]),
        ]
        F, R = 0.0, 0.0
        for (Lx, Lz), M in lastfaelle:
            Fi = M / hebel
            F = max(F, Fi)
            R = max(R, math.hypot(-Fi * ux - Lx, -Fi * uz - Lz))
        out.append({"winkel": a, "ok": True, "n": n, "F": F, "R": R,
                    "neigung": math.degrees(math.atan2(uz, -ux))})
    return out, s + l, F_last


def bock(p, d):
    """Sitz: je Winkel ein Klappbügel (ineinander geschachtelt). Höhe über dem Deckel und Kräfte."""
    tl, q, me, last = d["teile"]["sitz"], p["sitz"], p["mechanik"], p["last"]
    vb = -(d["polster_h"] - me["achse_unter_oberkante"])      # Unterseite Sitzplatte relativ zur Achse
    F_last = q["last_anteil"] * last["nutzer_kg"] * G * last["dynamik"]
    stufen, fehler = [], []
    for i, a in enumerate(tl["winkel"]):
        r = math.radians(a)
        u_i = q["bock_abstand"] - i * q["stufe"]
        u = (u_i + vb * math.sin(r)) / math.cos(r)
        h = d["achse_z"] + u * math.sin(r) + vb * math.cos(r) - d["deckel_z1"]
        M = F_last * q["last_abstand"]                          # ungünstiger Fall: Last senkrecht aufs Polster
        F = M / u_i
        stufen.append({"winkel": a, "u": u_i, "h": h, "F": F, "R": math.hypot(F_last - F, 0)})
    for s_ in stufen:
        if s_["u"] - s_["h"] - 10 < tl["u0"]:
            fehler.append(f"Bügel {s_['winkel']}° zu hoch, er passt umgeklappt nicht unter den Sitz")
    return stufen, q["bock_abstand"], F_last, fehler


def pruefe_rasten(p, d, teil, rs, park):
    tl, me = d["teile"][teil], p["mechanik"]
    fehler = [f"{r['winkel']}°: Stütze zu kurz" for r in rs if not r["ok"]]
    pos = sorted([r["n"] for r in rs if r["ok"]] + [park])
    lo, hi = tl["u0"] + 10, tl["u1"] - 10
    if pos and (pos[0] < lo or pos[-1] > hi):
        fehler.append(f"Rasten außerhalb der Leiste ({fmt(pos[0], 0)}–{fmt(pos[-1], 0)} mm, erlaubt {fmt(lo, 0)}–{fmt(hi, 0)} mm)")
    abst = min((b_ - a_ for a_, b_ in zip(pos, pos[1:])), default=999)
    if abst < me["min_rastabstand"]:
        fehler.append(f"Rasten zu dicht ({fmt(abst, 0)} mm < {me['min_rastabstand']} mm)")
    return fehler, abst


def suche_stuetze(p, d):
    """Sucht je Klappteil Anlenkpunkt und Länge der Stütze mit kleinster Stützkraft."""
    for teil in ("lehne",):
        tl = d["teile"][teil]
        treffer = []
        for s in range(60, int(tl["laenge"]), 10):
            for l in range(60, int(tl["laenge"]), 10):
                rs, park, _ = rasten(p, d, teil, s, l)
                if not pruefe_rasten(p, d, teil, rs, park)[0]:
                    treffer.append((max(r["F"] for r in rs), s, l))
        treffer.sort()
        print(f"[{teil}] Winkel {tl['winkel']}, Länge {tl['laenge']} mm – beste Stützen (max. Stützkraft, Abstand, Länge):")
        for F, s, l in treffer[:6]:
            print(f"  {F:6.0f} N   stuetze_abstand = {s}   stuetze_laenge = {l}")
        if not treffer:
            print("  keine Lösung – Winkel oder Länge ändern")


def hanteln(p):
    """Kopflänge je Hantel aus dem Zielgewicht: Stahlköpfe mit Abflachung und Fasen, Eichengriff, M16-Kern."""
    h = p["hanteln"]
    rs_, rg = h["dichte_stahl"] * 1e-9, h["dichte_griff"] * 1e-9
    gl, gd, kd, ab, fa = h["griff_laenge"], h["griff_d"], h["kern_d"], h["abflachung"], h["fase"]
    m_griff = math.pi / 4 * kd ** 2 * gl * rs_ + math.pi / 4 * (gd ** 2 - kd ** 2) * gl * rg
    out = []
    for kg, D in h["satz"]:
        R = D / 2
        seg = R * R * math.acos((R - ab) / R) - (R - ab) * math.sqrt(2 * R * ab - ab * ab) if ab else 0
        A = math.pi * R * R - seg
        m_kopf = (kg - m_griff) / 2
        lk = m_kopf / (A * rs_) + math.pi * D * fa ** 2 / A   # Fasenvolumen ausgleichen
        out.append({"kg": kg, "D": D, "lk": lk, "laenge": gl + 2 * lk, "m_kopf": m_kopf,
                    "kern_l": gl + 2 * h["gewinde_tiefe"], "liegehoehe": D - ab})
    return out, m_griff


def pack(p, d, hs):
    """Verteilt Hanteln und Inventar auf die Zellen (schwerste Teile zuerst, unten zuerst)."""
    gap = p["inventar"]["abstand"]
    ah = p["korpus"]["ablage_h"]
    items = [{"name": f"Kurzhanteln {fmt(x['kg'])} kg (Paar)", "typ": "khr", "kg": 2 * x["kg"],
              "w": 2 * x["D"] + gap, "h": x["liegehoehe"] + ah, "d": x["laenge"],
              "kopf": x["D"], "kopf_l": x["lk"]} for x in hs]
    for it in p.get("inhalt", []):
        items.append({**it, "w": it["breite"], "h": it["hoehe"], "d": it["tiefe"]})
    items.sort(key=lambda i: -i["kg"])

    belegt = {z["name"]: gap for z in d["zellen"]}
    platz, fehlt = [], []
    for it in items:
        for z in d["zellen"]:
            if (belegt[z["name"]] + it["w"] + gap <= z["breite"]
                    and it["h"] + 10 <= z["zugang"]
                    and it["d"] <= z["tiefe"]):
                x = z["x0"] + belegt[z["name"]]
                y = d["fach_y0"] + (z["tiefe"] - it["d"]) / 2
                platz.append({**it, "zelle": z["name"], "fach": z["fach"],
                              "ebene": z["ebene"], "x": x, "y": y, "z": z["z0"]})
                belegt[z["name"]] += it["w"] + gap
                break
        else:
            fehlt.append(it)
    return platz, fehlt, belegt


def scad_value(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, str):
        return '"' + v.replace('"', '\\"') + '"'
    if isinstance(v, (list, tuple)):
        return "[" + ", ".join(scad_value(x) for x in v) + "]"
    if isinstance(v, float):
        return f"{v:.3f}".rstrip("0").rstrip(".")
    return str(v)


def write_scad(p, d, platz, rast):
    k, rt, ro, po, me = p["korpus"], p["rolltuer"], p["rollen"], p["polster"], p["mechanik"]
    werte = {k_: d[k_] for k_ in (
        "L", "D", "H", "R", "t", "ti", "polster_h", "polster_z0", "rand_top", "deckel_z0", "deckel_z1",
        "boden_z0", "boden_z1", "korpus_h", "innen_l", "innen_h",
        "pad_y0", "pad_b", "pad_r_aussen", "lehne_x0", "lehne_x1", "lehne_l", "sitz_x0", "sitz_x1",
        "rt_x0", "rt_x1", "rt_len", "rt_y0", "rt_n", "rt_b", "rt_hinten_y0",
        "fach_y0", "fach_y1", "fach_tiefe", "tasche_x0", "tasche_x1", "mw_x", "fach_x0", "fach_breiten",
        "fuss_pos", "rollen_pos", "pedal_x",
        "achse_z", "vA", "rast_z", "park_tiefe", "leiste_y0", "bein_y0", "stab_y0", "stab_l", "rippe_y0")}
    werte.update({
        "polster_platte": po["platte"], "polster_r": po["radius"], "rand": po["rand"],
        "sockel_h": k["sockel_hoehe"], "sockel_einzug": k["sockel_einzug"],
        "fuss_d": k["fuss_d"], "fuss_h": k["fuss_h"], "ablage_h": k["ablage_h"],
        "fachboden": k["fachboden"],
        "fachboden_z0": d["fachboden_z0"] or 0, "fachboden_z1": d["fachboden_z1"] or 0,
        "rt_fuge": rt["lamelle_fuge"], "rt_dicke": rt["lamelle_dicke"],
        "buegel_d": me["buegel_d"], "rast_tiefe": me["rast_tiefe"], "leiste_b": me["leiste_breite"],
        "bein_b": me["bein_breite"], "bein_t": me["bein_dicke"],
        "rippe_b": me["rippe_breite"], "rippe_h": me["rippe_hoehe"],
        "gelenkplatte": me["gelenkplatte"],
        "rolle_d": ro["durchmesser"],
        # [typ, x, y, z, breite, hoehe, tiefe, kopf, kopflänge]
        "inhalt": [[i["typ"], i["x"], i["y"], i["z"], i["w"], i["h"], i["d"], i.get("kopf", 0), i.get("kopf_l", 0)]
                   for i in platz],
        "abstand": p["inventar"]["abstand"],
        "abflachung": p["hanteln"]["abflachung"], "griff_d": p["hanteln"]["griff_d"],
    })
    for teil in TEILE:
        tl = d["teile"][teil]
        werte.update({f"{teil}_achse_x": tl["achse_x"], f"{teil}_dir": tl["dir"], f"{teil}_laenge": tl["laenge"],
                      f"{teil}_winkel_liste": tl["winkel"],
                      f"{teil}_leiste_x0": tl["leiste_x0"], f"{teil}_leiste_x1": tl["leiste_x1"]})
    rs, park, _ = rast["lehne"]
    werte.update({"lehne_s": d["teile"]["lehne"]["s"], "lehne_l_stuetze": d["teile"]["lehne"]["l"],
                  "lehne_rasten": [r_["n"] for r_ in rs if r_["ok"]], "lehne_park": park,
                  "lehne_rippe_l": d["teile"]["lehne"]["rippe_l"]})
    stufen, gelenk, _, _ = rast["sitz"]
    werte.update({"sitz_stufen": [[s_["u"], s_["h"]] for s_ in stufen], "sitz_bock_gelenk": gelenk})
    lines = ["// AUTOMATISCH ERZEUGT von tools/build.py aus params.toml – nicht von Hand ändern.", ""]
    lines += [f"{k_} = {scad_value(v)};" for k_, v in werte.items()]
    (ROOT / "cad" / "params.scad").write_text("\n".join(lines) + "\n")


def teile(p, d):
    """Zuschnittliste: (Gruppe, Bezeichnung, Anzahl, Länge, Breite, Dicke, Hinweis)."""
    t, ti, R, L, D = d["t"], d["ti"], d["R"], d["L"], d["D"]
    k, rt, po, me = p["korpus"], p["rolltuer"], p["polster"], p["mechanik"]
    se, sh, fh = k["sockel_einzug"], k["sockel_hoehe"], k["fuss_h"]
    lb, le = d["teile"]["lehne"], d["teile"]["sitz"]
    massiv, platte, metall = "Eiche massiv", "Multiplex eichefurniert", "Stahl und Beschläge"
    return [
        (massiv, "Deckel", 1, L - 2 * t, D - 2 * t, t, f"Ecken R {R - t}, Laufnut Rolltür {rt['nut']} × {rt['nut']} (Tasche, hinten)"),
        (massiv, "Boden", 1, L - 2 * t, D - 2 * t, t, f"Ecken R {R - t}, Laufnut Rolltür (Tasche, hinten)"),
        (massiv, "Stirnseite", 2, d["korpus_h"], D - 2 * R, t, "Faser senkrecht, zwischen den Eckstollen"),
        (massiv, "Eckstollen", 4, d["korpus_h"], R, R, f"aus Massivholz verleimt, außen R {R} / innen R {R - t} ausgeformt, Faser senkrecht"),
        (massiv, "Frontleiste oben", 1, L - 2 * R, po["rand"] + t, t, "bildet vorn den Rand der Polsterwanne, Laufnut unten"),
        (massiv, "Frontleiste unten", 1, L - 2 * R, t, t, "Laufnut oben"),
        (massiv, "Rolltür-Lamelle", d["rt_n"], d["rt_lamelle_l"], round(d["rt_b"], 1), rt["lamelle_dicke"],
         f"Vorderseite gerundet (Kannelur), Zapfen oben/unten, auf Leinen geleimt, Fuge {fmt(rt['lamelle_fuge'])}"),
        (massiv, "Rastleiste Lehne", 2, lb["leiste_x1"] - lb["leiste_x0"], me["leiste_breite"], po["rand"], f"schwarz gebeizt, {len(lb['winkel'])} Rasten + Parkrast, verleimt"),
        (massiv, "Auflageleiste Sitz", 2, le["leiste_x1"] - le["leiste_x0"], me["leiste_breite"], po["rand"], "schwarz gebeizt, verleimt; die Klappbügel liegen dazwischen"),
        (massiv, "Lehnenrippe", 2, lb["rippe_l"], me["rippe_breite"], me["rippe_hoehe"], "unter der Lehnenplatte verleimt"),
        (massiv, "Polster-Anleimer", 1, round(2 * (d["lehne_l"] + po["sitz_laenge"] + 2 * d["pad_b"])), 8, po["platte"], "Gesamtlänge für beide Polsterplatten, sichtbare Eichenkante, Ecken gerundet"),
        (massiv, "Sockelzarge", 1, round(rr_umfang(L - 2 * se, D - 2 * se, R - se)), sh - fh, 20, f"umlaufend, Ecken R {R - se} (formverleimt oder gestäbt), Abwicklung"),
        (platte, "Rückwand", 1, L - 2 * R, d["korpus_h"], t, "Eichenfurnier stehend, Sichtseite zum Bett, zwischen den Eckstollen"),
        (platte, "Trennwand", d["n_mw"], d["fach_tiefe"], d["innen_h"], ti, "endet vor der hinteren Rolltürbahn"),
        *[(platte, f"Fachboden Fach {i + 1}", 1 if k["fachboden"] else 0, round(bb - 2, 1), d["fach_tiefe"] - 5, ti, "auf Bodenträgern")
          for i, bb in enumerate(d["fach_breiten"])],
        (platte, "Lehnenplatte", 1, d["lehne_l"], d["pad_b"], po["platte"], f"Ecken außen R {d['pad_r_aussen']}, Unterseite furniert"),
        (platte, "Sitzplatte", 1, po["sitz_laenge"], d["pad_b"], po["platte"], f"Ecken außen R {d['pad_r_aussen']}, Unterseite furniert"),
        (metall, "Gelenkplatte Korpus (2 Achsen)", 2, 110, 90, me["gelenkplatte"], "gelasert, 2 Bohrungen Ø 10,5 im Abstand der Fuge, Fuß 4 × M6 durch den Deckel"),
        (metall, "Gelenkplatte Lehne / Sitz", 4, 110, 70, me["gelenkplatte"], "gelasert, Lasche unter die Polsterplatte gekantet"),
        (metall, "Gegenplatte Flachstahl", 2, 140, 60, 6, "unter dem Deckel, nimmt Zugkräfte der Gelenke auf"),
        (metall, "Stütze Lehne: Bein", 2, lb["l"] + 30, me["bein_breite"], me["bein_dicke"], "Flachstahl, Bohrung Gelenk, mit Querstab verschweißt"),
        (metall, "Querstab Stütze Lehne", 1, round(d["stab_l"]), me["buegel_d"], me["buegel_d"], "Rundstahl"),
        *[(metall, f"Klappbügel Sitz {s_['winkel']}°", 1, round(s_["h"]), 240 - 24 * i, 8,
            "U-Bügel Flachstahl 30 × 8, Auflage gummiert, Scharnier auf dem Deckel; liegt sonst flach in der Wanne")
          for i, s_ in enumerate(reversed(bock(p, d)[0]))],
        (metall, "Absenkrolle (lenkbare Doppelrolle)", p["rollen"]["anzahl"], p["rollen"]["durchmesser"], p["rollen"]["durchmesser"], 0, "auf Hubplatte, parkettgeeignet"),
        (metall, "Exzenterwelle mit Hubnocken", 1, L - 2 * (k["fuss_einzug"] + 90) + 80, 20, 20, "läuft im Sockel, hebt alle 4 Rollen gleichzeitig"),
        (metall, "Fußhebel Bronze", 1, 90, 30, 6, "rastet oben (steht) und unten (rollt) über Totpunkt"),
    ]


def ei(rects):
    """Verbundquerschnitt aus Rechtecken (Breite, Höhe, z-Unterkante, E) → EI und Schwerpunkt.
    Aussparungen werden mit negativem E abgezogen."""
    EA = sum(E * b * h for b, h, _, E in rects)
    zs = sum(E * b * h * (z0 + h / 2) for b, h, z0, E in rects) / EA
    EI = sum(E * (b * h ** 3 / 12 + b * h * (z0 + h / 2 - zs) ** 2) for b, h, z0, E in rects)
    return EI, zs


def statik(p, d, platz, rast):
    m, last, me, k, po = p["material"], p["last"], p["mechanik"], p["korpus"], p["polster"]
    t, Em, Ep = d["t"], m["E_massiv"], m["E_platte"]
    F = last["nutzer_kg"] * G * last["dynamik"]
    res = []

    # 1. Vorderkante: Frontleiste oben (Rand) + Deckelstreifen + Rastleiste, Laufnut abgezogen
    nut = p["rolltuer"]["nut"]
    rects = [(t, t + po["rand"], 0, Em), (nut, nut, 0, -Em),
             (100 - t, t, 0, Em),
             (me["leiste_breite"], po["rand"] - me["rast_tiefe"], t, Em)]
    EI, _ = ei(rects)
    l = max(d["fach_breiten"]) + d["ti"]
    res.append(("Vorderkante: Frontleiste mit Rand + Deckel + Rastleiste (50 % der Last)", 0.5 * F, l,
                0.5 * F * l ** 3 / (48 * EI)))

    # 2. Lehnenplatte flach auf den Rastleisten (Rippen nicht angesetzt)
    l2 = d["leiste_y0"][1] - d["leiste_y0"][0]
    I2 = 300 * po["platte"] ** 3 / 12
    res.append(("Lehnenplatte flach zwischen den Rastleisten (Streifen 300 mm)", F, l2,
                5 * F * l2 ** 3 / (384 * Ep * I2)))

    # 3. Klappteile schräg: Überstand hinter dem Stützengelenk
    for teil in TEILE:
        tl = d["teile"][teil]
        F_last = rast[teil][2]
        a = tl["laenge"] - tl["s"]
        rects3 = [(d["pad_b"], po["platte"], 0, Ep)]
        if teil == "lehne":
            rects3.append((2 * me["rippe_breite"], me["rippe_hoehe"], -me["rippe_hoehe"], Em))
        EI3, _ = ei(rects3)
        q = F_last * math.cos(math.radians(min(tl["winkel"]))) / tl["laenge"]
        res.append((f"{NAME[teil]} schräg, Überstand hinter der Stütze ({min(tl['winkel'])}°)", q * a, a,
                    q * a ** 4 / (8 * EI3)))

    # 4. Fachböden mit dem Inhalt der oberen Ebene
    if k["fachboden"]:
        for f, bb in enumerate(d["fach_breiten"]):
            kg = sum(i["kg"] for i in platz if i["fach"] == f and i["ebene"] == "oben")
            Ff = kg * G * 2
            I4 = (d["fach_tiefe"] - 5) * d["ti"] ** 3 / 12
            res.append((f"Fachboden Fach {f + 1} ({fmt(kg)} kg × 2)", Ff, bb,
                        5 * Ff * bb ** 3 / (384 * Ep * I4)))
    return res


def knicken(p, teil, d, F_max):
    me = p["mechanik"]
    I = me["bein_breite"] * me["bein_dicke"] ** 3 / 12
    F_cr = 2 * math.pi ** 2 * E_STAHL * I / d["teile"][teil]["l"] ** 2
    return F_cr, F_cr / F_max if F_max else 99


def gewicht(p, d):
    m, po, k, rt, me = p["material"], p["polster"], p["korpus"], p["rolltuer"], p["mechanik"]
    t, L, D, R = d["t"], d["L"], d["D"], d["R"]
    se, sh, fh = k["sockel_einzug"], k["sockel_hoehe"], k["fuss_h"]
    lb, le = d["teile"]["lehne"], d["teile"]["sitz"]
    ring = (rr_flaeche(L, D, R) - rr_flaeche(L - 2 * t, D - 2 * t, R - t)) * d["korpus_h"] \
        - d["rt_len"] * t * d["innen_h"]
    platten = 2 * rr_flaeche(L - 2 * t, D - 2 * t, R - t) * t
    lamellen = d["rt_n"] * d["rt_b"] * d["rt_lamelle_l"] * rt["lamelle_dicke"]
    leisten = sum(2 * (tl["leiste_x1"] - tl["leiste_x0"]) * me["leiste_breite"] * po["rand"] for tl in (lb, le))
    rippen = 2 * lb["rippe_l"] * me["rippe_breite"] * me["rippe_hoehe"]
    zarge = rr_umfang(L - 2 * se, D - 2 * se, R - se) * 20 * (sh - fh)
    v_massiv = ring + platten + lamellen + leisten + rippen + zarge
    v_platte = (d["n_mw"] * d["fach_tiefe"] * d["innen_h"] * d["ti"]
                + (sum(d["fach_breiten"]) * d["fach_tiefe"] * d["ti"] if k["fachboden"] else 0)
                + (po["sitz_laenge"] + d["lehne_l"]) * d["pad_b"] * po["platte"])
    holz = v_massiv * 1e-9 * m["dichte_massiv"] + v_platte * 1e-9 * m["dichte_platte"]
    schaum = (po["sitz_laenge"] + d["lehne_l"]) * d["pad_b"] * po["schaum"] * 1e-9 * 45
    stahl = 7850e-9 * (2 * 110 * 90 * me["gelenkplatte"] + 4 * 110 * 70 * me["gelenkplatte"] + 2 * 140 * 60 * 6
                       + 2 * (lb["l"] + 30) * me["bein_breite"] * me["bein_dicke"]
                       + d["stab_l"] * math.pi * (me["buegel_d"] / 2) ** 2) + 1.0 + 3.0   # + Sitzbock, Absenkmechanik
    rest = 1.5 + 1.5                                                                  # Leder, Beschläge
    # abgewickelte Flächen: Korpusmantel ohne Rückwand (Multiplex) + Deckel/Boden + Rolltür + Zarge + Leisten
    flaeche_massiv = (rr_umfang(L, D, R) * d["korpus_h"] - (L - 2 * R) * d["korpus_h"]
                      + 2 * rr_flaeche(L - 2 * t, D - 2 * t, R - t)
                      + rr_umfang(L - 2 * se, D - 2 * se, R - se) * (sh - fh)
                      + (leisten + rippen) / t) * 1e-6
    flaeche_platte = (d["n_mw"] * d["fach_tiefe"] * d["innen_h"] + sum(d["fach_breiten"]) * d["fach_tiefe"]
                      + (L - 2 * R) * d["korpus_h"] + (po["sitz_laenge"] + d["lehne_l"]) * d["pad_b"]) * 1e-6
    return {"holz": holz, "schaum": schaum, "stahl": stahl, "rest": rest,
            "leer": holz + schaum + stahl + rest,
            "flaeche_massiv": flaeche_massiv, "flaeche_platte": flaeche_platte}


def fmt(x, n=1):
    return f"{x:,.{n}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def zahl(x):
    return fmt(x, 0 if float(x).is_integer() else 1)


def write_stueckliste(p, d, liste, platz, gw):
    m = p["material"]
    inhalt = sum(i["kg"] for i in platz)
    kosten_massiv = gw["flaeche_massiv"] * 1.3 * m["preis_massiv_m2"]
    kosten_platte = gw["flaeche_platte"] * 1.15 * m["preis_platte_m2"]
    holz_k = kosten_massiv + kosten_platte
    out = ["# Stückliste", "",
           "> Automatisch erzeugt aus `params.toml` mit `python3 tools/build.py`. Nicht von Hand ändern.", ""]
    for gruppe in dict.fromkeys(g for g, *_ in liste):
        out += [f"## {gruppe}", "",
                "| Teil | Stk. | Länge | Breite | Dicke | Hinweis |",
                "|---|---:|---:|---:|---:|---|"]
        for g, name, n, l, b, dicke, hinweis in liste:
            if g == gruppe and n:
                out.append(f"| {name} | {n} | {zahl(l)} | {zahl(b)} | {zahl(dicke) if dicke else '–'} | {hinweis} |")
        out.append("")
    po = p["polster"]
    zug = 2 * (po["schaum"] + 60)
    leder = ((po["sitz_laenge"] + zug) * (d["pad_b"] + zug) + (d["lehne_l"] + zug) * (d["pad_b"] + zug)) * 1e-6
    out += ["Maße in mm. Massivholz: Länge = Faserrichtung.", "",
            "## Polster", "",
            f"- Schaumstoff je Polster {po['schaum']} mm: 30 mm hart (RG 50+) unten, 20 mm mittel (RG 35–40) oben",
            "- Polyesterwatte 200 g/m² über den Schaum, damit die Kanten weich und voll wirken",
            f"- Bezug: ca. {fmt(leder, 2)} m² Rindleder, vollnarbig, pigmentiert oder Semianilin mit Schutzfinish "
            "(kein Anilin- oder Nubukleder: nimmt Schweiß auf), 1,2–1,5 mm, Kedernaht an der Oberkante",
            "- Das Leder endet oben an der Polsterplatte, die Eichenkante darunter bleibt sichtbar (wie im Bildentwurf)", "",
            "## Kleinteile", "",
            "| Teil | Menge | Zweck |", "|---|---:|---|",
            "| Domino-/Lamello-Verbinder | ca. 50 | Korpus, Eckstollen, Einbauten |",
            "| Holzleim D3 | 1 | feuchtebeständig (Schweiß, Wischen) |",
            "| Leinen/Baumwollgewebe + Leim | ca. 1,3 × 0,3 m | Rücken der Rolltür |",
            "| Gelenkbolzen M10 mit Gleitlagerbuchse, Hutmutter | 4 | Drehachsen von Lehne und Sitz |",
            "| Lagerböcke, Bolzen M8 | 4 | Gelenke der beiden Stützen |",
            "| Schrauben M6 durchgehend + Einschlagmuttern | 12 | Gelenkplatten, lösbar |",
            f"| Bodenträger 5 mm | {4 * d['n_fach'] if p['korpus']['fachboden'] else 0} | Fachböden |",
            f"| Füße Ø {p['korpus']['fuss_d']} × {p['korpus']['fuss_h']}, schwarz, mit Filz | 4 | unter der Sockelzarge |",
            "| Hantelablage: Flachstahl schwarz mit Mulden, filzbelegt | 4 | Ebenen der Hantelfächer |",
            "| Hartwachsöl | 0,75 l | Oberfläche |",
            "| Beize schwarz | 0,1 l | Rastleisten |", "",
            "## Gewicht und Kosten (Schätzung)", "",
            f"- Holz {fmt(gw['holz'])} kg, Stahl inkl. Absenkmechanik {fmt(gw['stahl'])} kg, Schaum {fmt(gw['schaum'])} kg, Leder/Kleinteile {fmt(gw['rest'])} kg",
            f"- Bank leer: ca. **{fmt(gw['leer'])} kg**, mit Inventar ({fmt(inhalt)} kg): ca. **{fmt(gw['leer'] + inhalt)} kg**", "",
            "| Posten | Kosten |", "|---|---:|",
            f"| Eiche massiv, {fmt(gw['flaeche_massiv'], 2)} m² + 30 % Verschnitt à {m['preis_massiv_m2']} €/m² | ca. {fmt(kosten_massiv, 0)} € |",
            f"| Multiplex eichefurniert, {fmt(gw['flaeche_platte'], 2)} m² + 15 % à {m['preis_platte_m2']} €/m² | ca. {fmt(kosten_platte, 0)} € |",
            "| Leder, Schaum, Watte | 250–450 € |",
            "| Polsterei (Arbeit, beide Polster) | 250–450 € |",
            "| Metallbau: Gelenke, 2 Stützen, Gegenplatten | 250–550 € |",
            "| Absenkrollen-Mechanik mit Bronze-Fußhebel | 200–450 € |",
            "| Kleinteile, Füße, Öl | 100–150 € |",
            f"| **Material und Fremdleistungen** | **ca. {fmt(holz_k + 1050, 0)}–{fmt(holz_k + 2050, 0)} €** |",
            "| Schreiner-Arbeitszeit, grob 60–90 h (Rundungen, Rolltür, Mechanik – Richtwert) | 4.000–7.000 € |",
            f"| **Gesamt grob** | **ca. {fmt(holz_k + 5050, 0)}–{fmt(holz_k + 9050, 0)} €** |", "",
            "Ohne Hanteln (siehe hanteln.md). Preise sind grobe Annahmen und regional sehr verschieden.", ""]
    (ROOT / "docs" / "stueckliste.md").write_text("\n".join(out))
    return inhalt


def write_berechnung(p, d, platz, fehlt, belegt, gw, inhalt, rast, pruef):
    me, last, k, po, ro = p["mechanik"], p["last"], p["korpus"], p["polster"], p["rollen"]

    def ok(w, g):
        return "✅" if w <= g else "⚠️"

    out = ["# Berechnung", "",
           "> Automatisch erzeugt aus `params.toml` mit `python3 tools/build.py`. Nicht von Hand ändern.",
           "> Überschlagsrechnung zur Plausibilisierung, kein Statik-Nachweis.", "",
           "## Hauptmaße", "",
           f"- Außen: {d['L']} × {d['D']} × {d['H']} mm (L × T × H), Ecken im Grundriss R {d['R']}",
           f"- Polster {d['pad_b']} mm breit in einer Wanne mit {po['rand']} mm Rand: Rückenlehne {d['lehne_l']} mm, "
           f"Fuge {po['fuge']} mm, Sitz {po['sitz_laenge']} mm",
           f"- Rolltür {fmt(d['rt_len'], 0)} mm lang aus {d['rt_n']} Lamellen à {fmt(d['rt_b'])} mm. Offen läuft sie in die "
           f"Tasche links ({k['tasche']} mm) und hinter den Fächern entlang (Speicherweg {fmt(d['rt_speicher'], 0)} mm "
           + ("✅)" if d["rt_speicher"] >= d["rt_len"] else "⚠️ zu kurz)"),
           f"- Fächer: {', '.join(fmt(b_, 0) for b_ in d['fach_breiten'])} mm breit, {fmt(d['fach_tiefe'], 0)} mm tief", ""]

    for teil in ("lehne",):
        tl = d["teile"][teil]
        rs, park, F_last = rast[teil]
        rfehler, rabst = pruef[teil]
        q = p[teil]
        seite = "linke" if tl["dir"] < 0 else "rechte"
        out += [f"## {NAME[teil]}", "",
                f"Drehachse an der inneren Kante, {me['achse_unter_oberkante']} mm unter der Polsteroberfläche "
                f"(x = {fmt(tl['achse_x'], 0)} mm ab linkem Ende). Das {seite} Ende hebt sich. "
                f"Die Stütze ist {tl['s']} mm von der Achse angelenkt und {tl['l']} mm lang.", "",
                f"Last: {int(q['last_anteil'] * 100)} % von {last['nutzer_kg']} kg × {last['dynamik']} = {fmt(F_last, 0)} N, "
                f"{q['last_abstand']} mm von der Achse, senkrecht nach unten oder senkrecht auf das Polster. "
                "Die Tabelle zeigt den ungünstigeren Fall.", "",
                "| Stellung | Rast ab Achse | Rast ab linkem Ende | Stützkraft | Achskraft | Neigung Stütze |",
                "|---|---:|---:|---:|---:|---:|",
                f"| 0° flach (Parkrast, {fmt(d['park_tiefe'], 0)} mm tief) | {fmt(park, 0)} mm | {fmt(gx(tl, park), 0)} mm | – | – | 0° |"]
        for r in rs:
            if r["ok"]:
                out.append(f"| {r['winkel']}° | {fmt(r['n'], 0)} mm | {fmt(gx(tl, r['n']), 0)} mm | "
                           f"{fmt(r['F'], 0)} N | {fmt(r['R'], 0)} N | {fmt(r['neigung'], 0)}° |")
            else:
                out.append(f"| {r['winkel']}° | – | – | – | – | Stütze zu kurz |")
        F_max = max((r["F"] for r in rs if r["ok"]), default=0)
        F_cr, sk = knicken(p, teil, d, F_max)
        out += ["",
                f"- Kleinster Abstand zwischen zwei Rasten {fmt(rabst, 0)} mm (Minimum {me['min_rastabstand']} mm).",
                f"- Knicken der Stütze (2 × Flachstahl {me['bein_breite']} × {me['bein_dicke']}): "
                f"Knicklast {fmt(F_cr / 1000, 1)} kN bei max. {fmt(F_max / 1000, 2)} kN → Sicherheit ≈ {fmt(sk, 1)}.",
                f"- Achskraft auf zwei Bolzen M10: Scherspannung ≈ {fmt(max((r['R'] for r in rs if r['ok']), default=0) / 2 / (math.pi * 25), 0)} N/mm² (zulässig > 100 N/mm²).",
                "", ("**⚠️ Geometrie prüfen:** " + "; ".join(rfehler)) if rfehler
                else "✅ Alle Rasten liegen auf der Leiste und haben genug Abstand.", ""]
    out += ["Bei steilen Stellungen zieht die Achse nach oben. Die Gelenkplatten werden deshalb mit durchgehenden "
            "Schrauben auf eine Stahl-Gegenplatte unter dem Deckel geschraubt.", ""]
    tl, q = d["teile"]["sitz"], p["sitz"]
    stufen, gelenk, F_last, sfehler = rast["sitz"]
    out += ["## Sitz", "",
            f"Drehachse an der inneren Kante (x = {fmt(tl['achse_x'], 0)} mm ab linkem Ende), {p['mechanik']['achse_unter_oberkante']} mm "
            "unter der Polsteroberfläche. Das rechte Ende hebt sich, damit man auf der Schrägbank nicht nach vorn rutscht. "
            "Getragen wird der Sitz von Klappbügeln aus Stahl, einer je Stellung, ineinander geschachtelt. "
            "Der benutzte Bügel wird hochgeklappt und steht senkrecht, die anderen liegen flach in der Wanne.", "",
            f"Last: {int(q['last_anteil'] * 100)} % von {last['nutzer_kg']} kg × {last['dynamik']} = {fmt(F_last, 0)} N, "
            f"{q['last_abstand']} mm von der Achse, senkrecht auf das Polster.", "",
            "| Stellung | Bügel ab Achse | Bügelhöhe über Deckel | Kraft auf den Bügel | Achskraft |",
            "|---|---:|---:|---:|---:|",
            "| 0° flach | – | alle Bügel liegen flach | – | – |"]
    for s_ in stufen:
        out.append(f"| {s_['winkel']}° | {fmt(s_['u'], 0)} mm | {fmt(s_['h'], 0)} mm | {fmt(s_['F'], 0)} N | {fmt(s_['R'], 0)} N |")
    out += ["", ("**⚠️ Geometrie prüfen:** " + "; ".join(sfehler)) if sfehler
            else "✅ Die Bügel passen umgeklappt unter den Sitz.", ""]

    out += ["## Stauraum-Belegung", "",
            "Schwerste Teile zuerst, untere Ebene zuerst. Die Hanteln liegen auf einer schwarzen Ablage.", "",
            "| Zelle | Inhalt | Breite | Höhe | Tiefe | kg |", "|---|---|---:|---:|---:|---:|"]
    for i in sorted(platz, key=lambda i: (i["fach"], i["ebene"] == "oben")):
        out.append(f"| {i['zelle']} | {i['name']} | {fmt(i['w'], 0)} | {fmt(i['h'], 0)} | {fmt(i['d'], 0)} | {fmt(i['kg'])} |")
    out += ["", "| Zelle | lichte Höhe | belegt / verfügbar (Breite) | davon vorn offen |", "|---|---:|---:|---:|"]
    for z in sorted(d["zellen"], key=lambda z: (z["fach"], z["ebene"] == "oben")):
        out.append(f"| {z['name']} | {fmt(z['zugang'], 0)} mm | {fmt(belegt[z['name']], 0)} / {fmt(z['breite'], 0)} mm | {fmt(z['offen'], 0)} mm |")
    out += ["", ("**⚠️ Passt nicht:** " + ", ".join(i["name"] for i in fehlt)) if fehlt
            else "✅ Alles Inventar findet Platz."]

    out += ["", "## Durchbiegung", "",
            f"Lastannahme: {last['nutzer_kg']} kg Nutzer × Stoßfaktor {last['dynamik']}.", "",
            "| Bauteil | Last | Stützweite | Durchbiegung | Grenze L/300 | |",
            "|---|---:|---:|---:|---:|---|"]
    for name, F, l, w in statik(p, d, platz, rast):
        out.append(f"| {name} | {fmt(F, 0)} N | {fmt(l, 0)} mm | {fmt(w, 2)} mm | {fmt(l / 300, 2)} mm | {ok(w, l / 300)} |")
    out += ["", "Die verleimte Rückwand trägt die Hinterkante des Deckels zusätzlich mit. Sie ist hier nicht angesetzt.", ""]

    fe, fd = k["fuss_einzug"], k["fuss_d"]
    stand = fe - fd / 2                      # äußere Kante der Füße
    ueber_y = max(stand - d["pad_y0"], 1)
    ueber_x = max(stand - d["lehne_x0"], 1)
    out += ["## Kippsicherheit", "",
            f"Die Bank steht auf 4 Füßen, deren Außenkante {fmt(stand, 0)} mm hinter der Korpuskante liegt. "
            f"Das Polster beginnt {d['pad_y0']} mm hinter der Kante.", "",
            "| Fall | leer | mit Inventar |", "|---|---:|---:|"]
    for label, hebel, ueber in (("Längskante", d["D"] / 2 - stand, ueber_y), ("Stirnkante", d["L"] / 2 - stand, ueber_x)):
        werte = [w * hebel / ueber for w in (gw["leer"], gw["leer"] + inhalt)]
        txt = ["> 1.000 kg (kippt praktisch nicht)" if w_ > 1000 else f"{fmt(w_, 0)} kg" for w_ in werte]
        out.append(f"| Senkrechte Last auf der {label}, ab der die Bank kippt | {txt[0]} | {txt[1]} |")
    lb = d["teile"]["lehne"]
    a_max = math.radians(max(lb["winkel"]))
    h_top = d["achse_z"] + lb["laenge"] * math.sin(a_max)
    hebel = d["L"] / 2 - stand
    kipp = [w * G * hebel / h_top for w in (gw["leer"], gw["leer"] + inhalt)]
    out.append(f"| Lehne {max(lb['winkel'])}°: waagerechter Druck nach hinten an der Lehnenoberkante ({fmt(h_top, 0)} mm hoch), niemand sitzt | "
               f"{fmt(kipp[0], 0)} N | {fmt(kipp[1], 0)} N |")
    mit_person = kipp[0] + last["nutzer_kg"] * G * ((d["sitz_x0"] + d["sitz_x1"]) / 2 - stand) / h_top
    out += ["",
            f"Sitzt jemand auf dem Sitz, steigt der letzte Wert (leere Bank) auf ≈ {fmt(mit_person, 0)} N. "
            "Beim Training ist das unkritisch. Die aufgestellte Lehne ist aber kein Griff zum Hochziehen, "
            "wenn die Bank leer ist.", ""]
    kraft = [(w * G * ro["hub"] / ro["pedalweg"] * 1.3) for w in (gw["leer"], gw["leer"] + inhalt)]
    out += ["## Absenkrollen: vom Bett abrücken", "",
            f"- {ro['anzahl']} lenkbare Doppelrollen Ø {ro['durchmesser']} mm sitzen verdeckt im Sockel. Eine Exzenterwelle hebt sie gemeinsam.",
            f"- Bronze-Fußhebel vorn rechts nach unten treten: Die Rollen fahren {ro['hub']} mm unter die Füße, und die Bank rollt in jede Richtung.",
            "  Hebel mit der Fußspitze hochziehen: Die Bank steht wieder fest auf den Füßen. Der Hebel rastet in beiden Lagen über den Totpunkt.",
            f"- Fußkraft am Hebel (≈ {ro['pedalweg']} mm Weg, mit Reibung): leer ≈ {fmt(kraft[0] / G, 0)} kg, mit Inventar ≈ {fmt(kraft[1] / G, 0)} kg.",
            "- Zum Training die Bank ca. 60 cm vom Bett wegrollen: Beim Drücken und bei Fliegenden gehen die Ellbogen unter Polsterhöhe, "
            "und auf der Schrägbank steht ein Fuß neben der Bank. Vor dem Training die Rollen hochstellen.",
            "- Die Rollen sind für glatte Böden (Parkett, Fliesen) gedacht.", ""]
    (ROOT / "docs" / "berechnung.md").write_text("\n".join(out))


def write_hanteln(p, hs, m_griff):
    h = p["hanteln"]
    rho = h["dichte_stahl"] * 1e-9
    roh_kg = sum(2 * math.pi / 4 * (x["D"] + 3) ** 2 * (x["lk"] + h["zugabe"] + 3) * rho for x in hs)
    ab = h["abflachung"]
    out = ["# Hanteln", "",
           "> Automatisch erzeugt aus `params.toml` mit `python3 tools/build.py`. Nicht von Hand ändern.", "",
           "Fünf Paar Kurzhanteln, passend zur Bank: schwarze Stahlköpfe, Griff aus Eiche. "
           "Die Maße sind so gewählt, dass jedes Paar genau in sein Fach passt "
           "(Belegung siehe [berechnung.md](berechnung.md)).", "",
           "![Hantel](zeichnungen/hantel.svg)", "",
           "## Aufbau", "",
           f"- **Köpfe:** Rundstahl S235, gedreht. Fase {h['fase']} × 45° an allen Kanten, zentrisches Sackloch M16 × {h['gewinde_tiefe']} mm"
           + (f", {ab} mm tiefe Abflachung. Mit ihr rollt die Hantel nicht weg und liegt stabil auf der Ablage." if ab else "."),
           f"- **Kern:** Gewindestange M16, Festigkeitsklasse 8.8. Sie hält beide Köpfe, die Eichenhülse wird dazwischen geklemmt.",
           f"- **Griff:** Eiche gedreht, Ø {h['griff_d']} mm, Bohrung 16,5 mm, Länge {h['griff_laenge']} mm. "
           "Optional mit feinen Längsrillen wie die Lamellen der Bank, das gibt Grip.",
           "- **Oberfläche:** Köpfe brüniert und gewachst (Patina gewollt) oder matt schwarz pulverbeschichtet. Griff geölt.",
           f"- **Gewicht Griff + Kern:** {fmt(m_griff * 1000, 0)} g, der Rest steckt in den Köpfen.", "",
           "## Maße", "",
           "| Hantel | Kopf Ø | Kopflänge | Hantel gesamt | Kopf je Stück | Gewindestange | Rohteil je Kopf (gesägt) | g je mm Kopflänge |",
           "|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for x in hs:
        R = x["D"] / 2
        A = math.pi * R * R
        if ab:
            A -= R * R * math.acos((R - ab) / R) - (R - ab) * math.sqrt(2 * R * ab - ab * ab)
        out.append(f"| {fmt(x['kg'])} kg | {x['D']} mm | {fmt(x['lk'])} mm | {fmt(x['laenge'], 0)} mm | "
                   f"{fmt(x['m_kopf'], 2)} kg | M16 × {x['kern_l']} | Ø {x['D'] + 3} × {fmt(x['lk'] + h['zugabe'] + 3, 0)} mm | "
                   f"{fmt(A * rho * 1000, 0)} g |")
    breite = [f"Ø {x['D']}: {fmt(2 * math.sqrt(2 * x['D'] / 2 * ab - ab * ab), 0)} mm" for x in hs] if ab else []
    out += ["", f"Je Gewicht wird ein Paar gebaut, also 10 Köpfe. Breite der Abflachung: {', '.join(dict.fromkeys(breite))}." if ab else "", "",
            "## Fertigung", "",
            f"1. **Rohteile:** Rundstahl S235 beim Stahlhandel auf Länge sägen lassen. Je Kopf Ø + 3 mm und Länge + {h['zugabe'] + 3} mm.",
            f"2. **Drehen** (Dreherei oder eigene Drehbank): Außen-Ø, Planflächen und Fasen. Zentrisch bohren (Ø 14) und Gewinde M16 × {h['gewinde_tiefe']} schneiden.",
            f"3. **Abflachung** {ab} mm tief fräsen." if ab else "3. –",
            f"4. **Auf Gewicht bringen:** Die Köpfe sind {h['zugabe']} mm länger gedreht. Hantel probehalber montieren, wiegen "
            "und an der Außenseite abplanen, bis das Gewicht stimmt (siehe Spalte g je mm). Toleranz ±1 %.",
            "5. **Oberfläche:** brünieren und wachsen, oder pulverbeschichten (Gewinde abdecken).",
            "6. **Griff:** Eiche drehen, eventuell Rillen fräsen, ölen.",
            "7. **Montage:** Gewindestange mit hochfester Schraubensicherung (z. B. Loctite 270) in den ersten Kopf drehen. "
            "Griff aufschieben, zweiten Kopf mit Sicherung aufdrehen, bis der Griff fest geklemmt ist. 24 h aushärten lassen.", "",
            "## Sicherheit", "",
            "- Die Köpfe dürfen sich nie lösen. Deshalb hochfeste Sicherung und eine Gewindestange der Klasse 8.8, keine Baumarkt-Gewindestange 4.6.",
            "- Den festen Sitz anfangs vor jedem Training prüfen, später monatlich.",
            "- Nicht fallen lassen: Stahl auf Parkett hinterlässt Dellen, und der Holzgriff kann reißen.", "",
            "## Kosten (Schätzung)", "",
            "| Posten | Kosten |", "|---|---:|",
            f"| Rundstahl, ca. {fmt(roh_kg, 0)} kg à {h['preis_stahl_kg']} €/kg | ca. {fmt(roh_kg * h['preis_stahl_kg'], 0)} € |",
            "| Dreherei: 10 Köpfe drehen, bohren, Gewinde, Abflachung | 250–450 € |",
            "| Brünieren oder Pulverbeschichten | 50–100 € |",
            "| Gewindestange M16 8.8, Eiche, Schraubensicherung, Öl | 30–50 € |",
            f"| **Gesamt** | **ca. {fmt(roh_kg * h['preis_stahl_kg'] + 330, 0)}–{fmt(roh_kg * h['preis_stahl_kg'] + 600, 0)} €** |", "",
            "Mit eigener Drehbank fallen die Dreherei-Kosten weg.", ""]
    (ROOT / "docs" / "hanteln.md").write_text("\n".join(out))


ANSICHTEN = [
    # Datei, Kamera (tx,ty,tz,rx,ry,rz,dist), Projektion, -D Optionen
    ("moebel.png", "700,215,230,72,0,22,2850", "p", {}),
    ("training.png", "700,215,330,70,0,22,3300", "p",
     {"lehne_winkel": "30", "sitz_winkel": "20", "rolltuer_offen": "true"}),
    ("schraeg.png", "700,215,480,70,0,22,3700", "p", {"lehne_winkel": "45"}),
    ("verstellung.png", "700,0,760,90,0,0,3300", "o",
     {"lehne_winkel": "45", "sitz_winkel": "10", "geist": "true", "zeige_inhalt": "false"}),
    ("stauraum.png", "700,215,230,72,0,22,2850", "p", {"rolltuer_offen": "true"}),
    ("explosion.png", "700,215,320,66,0,22,3800", "p", {"explosion": "1"}),
    ("moebel_nussbaum.png", "700,215,230,72,0,22,2850", "p", {"farbschema": '"nussbaum"'}),
]


def render():
    if not shutil.which("openscad"):
        print("OpenSCAD nicht gefunden – Renderings übersprungen.")
        return
    prefix = ["xvfb-run", "-a"] if shutil.which("xvfb-run") and sys.platform.startswith("linux") else []
    (ROOT / "renders").mkdir(exist_ok=True)
    for datei, cam, proj, defs in ANSICHTEN:
        cmd = prefix + ["openscad", "-o", str(ROOT / "renders" / datei), "--imgsize=1600,1000",
                        f"--camera={cam}", f"--projection={proj}", "--colorscheme=Tomorrow"]
        for k_, v in defs.items():
            cmd += ["-D", f"{k_}={v}"]
        cmd.append(str(ROOT / "cad" / "bank.scad"))
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            print(res.stderr)
            raise SystemExit(f"Rendern von {datei} fehlgeschlagen")
        print(f"  renders/{datei}")


def main():
    p = load_params()
    d = derive(p)
    if "--stuetze-suchen" in sys.argv:
        suche_stuetze(p, d)
        return
    rast = {"lehne": rasten(p, d, "lehne"), "sitz": bock(p, d)}
    pruef = {"lehne": pruefe_rasten(p, d, "lehne", rast["lehne"][0], rast["lehne"][1]),
             "sitz": (rast["sitz"][3], None)}
    hs, m_griff = hanteln(p)
    platz, fehlt, belegt = pack(p, d, hs)
    write_scad(p, d, platz, rast)
    gw = gewicht(p, d)
    inhalt = write_stueckliste(p, d, teile(p, d), platz, gw)
    write_berechnung(p, d, platz, fehlt, belegt, gw, inhalt, rast, pruef)
    write_hanteln(p, hs, m_griff)
    zeichnungen.erzeuge(ROOT / "docs" / "zeichnungen", p, d, rast, hs)
    print("cad/params.scad, docs/stueckliste.md, docs/berechnung.md, docs/hanteln.md, docs/zeichnungen/ geschrieben")
    for teil in TEILE:
        for w in pruef[teil][0]:
            print(f"WARNUNG {NAME[teil]}:", w)
    if fehlt:
        print("WARNUNG – passt nicht in den Stauraum:", ", ".join(i["name"] for i in fehlt))
    if "--no-render" not in sys.argv:
        render()


if __name__ == "__main__":
    main()
