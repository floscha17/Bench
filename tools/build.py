#!/usr/bin/env python3
"""Erzeugt aus params.toml alle abgeleiteten Dateien der Bank.

- cad/params.scad       Parameter + abgeleitete Maße für das OpenSCAD-Modell
- docs/stueckliste.md   Zuschnittliste, Metallteile, Beschläge, Gewicht, grobe Kosten
- docs/berechnung.md    Schrägbank-Rasten, Stauraum, Durchbiegung, Kippsicherheit
- renders/*.png         Ansichten (nur wenn OpenSCAD installiert ist)

Aufruf:  python3 tools/build.py [--no-render]
"""

import math
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
G = 9.81
E_STAHL = 210000


def load_params():
    with open(ROOT / "params.toml", "rb") as f:
        return tomllib.load(f)


def derive(p):
    """Alle abgeleiteten Maße an einer Stelle – SCAD und Doku nutzen dieselben Werte."""
    b, m, po, sb, k, tu = (p["bank"], p["material"], p["polster"], p["schraegbank"],
                           p["korpus"], p["tueren"])
    L, D, H = b["laenge"], b["tiefe"], b["hoehe"]
    t, ti, tr = m["aussen"], m["innen"], m["rueckwand"]
    d = {"L": L, "D": D, "H": H, "t": t, "ti": ti, "tr": tr}

    # Höhenaufbau von oben: Polster → Schattenfuge → Deckel → Fächer → Boden → Sockel
    P = po["platte"] + po["schaum"]
    d["polster_h"] = P
    d["polster_z0"] = H - P
    d["deckel_z1"] = d["polster_z0"] - po["schattenfuge"]
    d["deckel_z0"] = d["deckel_z1"] - t
    d["boden_z0"] = k["sockel_hoehe"]
    d["boden_z1"] = d["boden_z0"] + t
    d["korpus_h"] = d["deckel_z1"] - d["boden_z0"]
    d["innen_l"] = L - 2 * t
    d["innen_h"] = d["deckel_z0"] - d["boden_z1"]

    # Polster: fester Sitz links, Rückenlehne rechts, rundum eingerückt
    e = po["einzug"]
    d["pad_y0"], d["pad_b"] = e, D - 2 * e
    d["sitz_x0"], d["sitz_x1"] = e, e + po["sitz_laenge"]
    d["lehne_x0"] = d["sitz_x1"] + po["fuge"]
    d["lehne_x1"] = L - e
    d["lehne_l"] = d["lehne_x1"] - d["lehne_x0"]

    # Schiebetüren aus Lamellen, zwei Laufspuren
    tt = tu["lamelle_dicke"] + tu["traverse_dicke"]
    d["tuer_t"] = tt
    d["tuer_y0"] = [2, 2 + tt + tu["spur_luft"]]
    d["fach_y0"] = d["tuer_y0"][1] + tt + tu["spur_luft"]
    d["rueck_y0"] = D - 10 - tr
    d["fach_tiefe"] = d["rueck_y0"] - d["fach_y0"]
    n_t = tu["anzahl"]
    d["n_tuer"] = n_t
    d["tuer_l"] = (d["innen_l"] + (n_t - 1) * tu["ueberlappung"]) / n_t
    d["tuer_x0"] = [t + i * (d["tuer_l"] - tu["ueberlappung"]) for i in range(n_t)]
    d["tuer_z0"] = d["boden_z1"] + 1
    # Lamellen reichen bis 2 mm unter den Deckel; oben führt eine Feder der Traverse in einer Deckelnut
    d["tuer_h"] = d["deckel_z0"] - 2 - d["tuer_z0"]
    n_lam = round((d["tuer_l"] + tu["lamelle_fuge"]) / (tu["lamelle_breite"] + tu["lamelle_fuge"]))
    d["n_lamellen"] = n_lam
    d["lamelle_b"] = (d["tuer_l"] - (n_lam - 1) * tu["lamelle_fuge"]) / n_lam

    # Fächer
    n_mw = k["mittelwaende"]
    d["n_mw"], d["n_fach"] = n_mw, n_mw + 1
    d["fach_breite"] = (d["innen_l"] - n_mw * ti) / d["n_fach"]
    d["fach_x0"] = [t + i * (d["fach_breite"] + ti) for i in range(d["n_fach"])]
    if k["fachboden"]:
        d["fachboden_z0"] = d["boden_z1"] + k["fach_unten"]
        d["fachboden_z1"] = d["fachboden_z0"] + ti
    else:
        d["fachboden_z0"] = d["fachboden_z1"] = None

    zellen = []
    for i, x0 in enumerate(d["fach_x0"]):
        if k["fachboden"]:
            ebenen = [("unten", d["boden_z1"], d["fachboden_z0"]),
                      ("oben", d["fachboden_z1"], d["deckel_z0"])]
        else:
            ebenen = [("", d["boden_z1"], d["deckel_z0"])]
        for ebene, z0, z1 in ebenen:
            zellen.append({
                "name": f"Fach {i + 1} {ebene}".strip(),
                "fach": i, "ebene": ebene, "x0": x0, "z0": z0,
                "h": z1 - z0, "zugang": z1 - z0,
                "breite": d["fach_breite"], "tiefe": d["fach_tiefe"],
            })
    zellen.sort(key=lambda z: (z["ebene"] == "oben", z["fach"]))
    d["zellen"] = zellen

    # Schrägbank: Drehachse an der Vorderkante der Lehne, knapp unter der Oberfläche
    d["achse_x"] = d["lehne_x0"]
    d["achse_z"] = H - sb["achse_unter_oberkante"]
    d["vA"] = -(P - sb["achse_unter_oberkante"]) - sb["stuetze_versatz"]
    r = sb["buegel_d"] / 2
    d["rast_z"] = d["polster_z0"] - sb["rast_tiefe"] + r - d["achse_z"]
    d["park_tiefe"] = d["polster_z0"] - (d["achse_z"] + d["vA"]) + r
    lb, le = sb["leiste_breite"], sb["leiste_einzug"]
    d["leiste_y0"] = [e + le, D - e - le - lb]
    d["leiste_x0"] = d["achse_x"] + 40
    d["leiste_x1"] = d["lehne_x1"] - 10
    d["bein_y0"] = [d["leiste_y0"][0] + lb + 2, d["leiste_y0"][1] - 2 - sb["bein_breite"]]
    d["stab_y0"] = d["leiste_y0"][0] + 5
    d["stab_l"] = d["leiste_y0"][1] + lb - 5 - d["stab_y0"]
    rippe_y = d["bein_y0"][0] + sb["bein_breite"] + 25
    d["rippe_y0"] = [rippe_y, D - rippe_y - sb["rippe_breite"]]
    d["rippe_l"] = sb["stuetze_abstand"] + sb["stuetze_laenge"] - 25 - 20
    return d


def rasten(p, d):
    """Raststellungen der Stütze: Position je Winkel, Stützkraft, Achskraft."""
    sb, last = p["schraegbank"], p["last"]
    s, l = sb["stuetze_abstand"], sb["stuetze_laenge"]
    vA, zN = d["vA"], d["rast_z"]
    F_last = sb["last_anteil"] * last["nutzer_kg"] * G * last["dynamik"]
    out = []
    for a in sb["winkel"]:
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
        # Lastfall 1: Gewicht senkrecht nach unten; Lastfall 2: Last senkrecht auf die Lehnenfläche
        # (Zurücklehnen, Drücken). Ausgegeben wird jeweils der ungünstigere Fall.
        lastfaelle = [
            ((0.0, -F_last), F_last * (sb["last_abstand"] * math.cos(r) - sb["achse_unter_oberkante"] * math.sin(r))),
            ((F_last * math.sin(r), -F_last * math.cos(r)), F_last * sb["last_abstand"]),
        ]
        F, R = 0.0, 0.0
        for (Lx, Lz), M in lastfaelle:
            Fi = M / hebel
            F = max(F, Fi)
            R = max(R, math.hypot(-Fi * ux - Lx, -Fi * uz - Lz))
        out.append({"winkel": a, "ok": True, "n": n, "F": F, "R": R,
                    "neigung": math.degrees(math.atan2(uz, -ux))})
    park = s + l
    return out, park, F_last


def pruefe_rasten(p, d, rs, park):
    sb = p["schraegbank"]
    fehler = [f"{r['winkel']}°: Stütze zu kurz" for r in rs if not r["ok"]]
    pos = sorted([r["n"] for r in rs if r["ok"]] + [park])
    lo, hi = d["leiste_x0"] - d["achse_x"] + 10, d["leiste_x1"] - d["achse_x"] - 10
    if pos and (pos[0] < lo or pos[-1] > hi):
        fehler.append(f"Rasten außerhalb der Leiste ({fmt(pos[0], 0)}–{fmt(pos[-1], 0)} mm, erlaubt {fmt(lo, 0)}–{fmt(hi, 0)} mm)")
    abst = min((b_ - a_ for a_, b_ in zip(pos, pos[1:])), default=999)
    if abst < sb["min_rastabstand"]:
        fehler.append(f"Rasten zu dicht ({fmt(abst, 0)} mm < {sb['min_rastabstand']} mm)")
    return fehler, abst


def pack(p, d):
    """Verteilt das Inventar auf die Zellen (schwerste Teile zuerst, unten zuerst)."""
    gap = p["inventar"]["abstand"]
    items = []
    for it in p["inhalt"]:
        if it["typ"] == "kh":
            w, h, dep = 2 * it["kopf"] + gap, it["kopf"], it["laenge"]
        else:
            w, h, dep = it["breite"], it["hoehe"], it["tiefe"]
        items.append({**it, "w": w, "h": h, "d": dep})
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


def write_scad(p, d, platz, rs, park):
    k, tu, r, po, sb = p["korpus"], p["tueren"], p["rollen"], p["polster"], p["schraegbank"]
    werte = {k_: d[k_] for k_ in (
        "L", "D", "H", "t", "ti", "tr", "polster_h", "polster_z0", "deckel_z0", "deckel_z1",
        "boden_z0", "boden_z1", "korpus_h", "innen_l", "innen_h",
        "pad_y0", "pad_b", "sitz_x0", "sitz_x1", "lehne_x0", "lehne_x1", "lehne_l",
        "tuer_t", "tuer_y0", "fach_y0", "rueck_y0", "fach_tiefe", "tuer_l", "tuer_x0", "tuer_z0",
        "tuer_h", "n_lamellen", "lamelle_b", "n_mw", "fach_breite", "fach_x0",
        "achse_x", "achse_z", "vA", "rast_z", "park_tiefe", "leiste_y0", "leiste_x0", "leiste_x1",
        "bein_y0", "stab_y0", "stab_l", "rippe_y0", "rippe_l")}
    werte.update({
        "polster_platte": po["platte"], "polster_r": po["radius"], "schattenfuge": po["schattenfuge"],
        "sockel_h": k["sockel_hoehe"], "sockel_einzug": k["sockel_einzug"],
        "fachboden": k["fachboden"],
        "fachboden_z0": d["fachboden_z0"] or 0, "fachboden_z1": d["fachboden_z1"] or 0,
        "lamelle_fuge": tu["lamelle_fuge"], "lamelle_dicke": tu["lamelle_dicke"],
        "traverse_dicke": tu["traverse_dicke"],
        "stuetze_s": sb["stuetze_abstand"], "stuetze_l": sb["stuetze_laenge"],
        "buegel_d": sb["buegel_d"], "rast_tiefe": sb["rast_tiefe"], "leiste_b": sb["leiste_breite"],
        "bein_b": sb["bein_breite"], "bein_t": sb["bein_dicke"],
        "rippe_b": sb["rippe_breite"], "rippe_h": sb["rippe_hoehe"],
        "gelenkplatte": sb["gelenkplatte"],
        "winkel": sb["winkel"],
        "rasten": [r_["n"] for r_ in rs if r_["ok"]], "park": park,
        "rollen": r["aktiv"], "rolle_d": r["durchmesser"], "rolle_b": r["breite"],
        "rolle_luft": r["bodenfreiheit"],
        # [typ, x, y, z, breite, hoehe, tiefe, kopf]
        "inhalt": [[i["typ"], i["x"], i["y"], i["z"], i["w"], i["h"], i["d"], i.get("kopf", 0)]
                   for i in platz],
        "abstand": p["inventar"]["abstand"],
    })
    lines = ["// AUTOMATISCH ERZEUGT von tools/build.py aus params.toml – nicht von Hand ändern.", ""]
    lines += [f"{k_} = {scad_value(v)};" for k_, v in werte.items()]
    (ROOT / "cad" / "params.scad").write_text("\n".join(lines) + "\n")


def teile(p, d):
    """Zuschnittliste: (Gruppe, Bezeichnung, Anzahl, Länge, Breite, Dicke, Hinweis)."""
    t, ti, tr = d["t"], d["ti"], d["tr"]
    k, tu, po, sb = p["korpus"], p["tueren"], p["polster"], p["schraegbank"]
    se, sh = k["sockel_einzug"], k["sockel_hoehe"]
    sf = po["schattenfuge"]
    massiv, platte, metall = "Eiche massiv", "Multiplex eichefurniert", "Stahl"
    return [
        (massiv, "Deckel", 1, d["L"], d["D"], t, "Gehrung links/rechts, Nut für Rückwand"),
        (massiv, "Boden", 1, d["L"], d["D"], t, "Gehrung links/rechts, Laufnuten, Nut für Rückwand"),
        (massiv, "Seitenwange", 2, d["korpus_h"], d["D"], t, "Gehrung oben/unten – alle 4 aus einem Brett für umlaufende Maserung"),
        (massiv, "Türlamelle", d["n_tuer"] * d["n_lamellen"], d["tuer_h"], round(d["lamelle_b"], 1), tu["lamelle_dicke"], "Vorderkanten gerundet R3"),
        (massiv, "Türtraverse", 2 * d["n_tuer"], round(d["tuer_l"], 1), 40, tu["traverse_dicke"], f"verdeckt hinter den Lamellen, obere mit {tu['nut_oben']} mm Feder"),
        (massiv, "Rastleiste", 2, d["leiste_x1"] - d["leiste_x0"], sb["leiste_breite"], sf, f"schwarz gebeizt, mit dem Deckel verleimt, {len(sb['winkel'])} Rasten + Parkrast"),
        (massiv, "Lehnenrippe", 2, d["rippe_l"], sb["rippe_breite"], sb["rippe_hoehe"], "unter der Lehnenplatte verleimt"),
        (massiv, "Sitz-Distanzleiste", 4, po["sitz_laenge"] - 50, 20, sf, "schwarz gebeizt, mit dem Deckel verleimt (versteift die Vorderkante)"),
        (massiv, "Sockel längs", 2, d["L"] - 2 * se, sh, t, "schwarz gebeizt"),
        (massiv, "Sockel quer", 2, d["D"] - 2 * se - 2 * t, sh, t, "schwarz gebeizt"),
        (platte, "Mittelwand", d["n_mw"], d["fach_tiefe"], d["innen_h"], ti, "Bohrreihe für Bodenträger"),
        (platte, "Fachboden", d["n_fach"] if k["fachboden"] else 0, round(d["fach_breite"] - 2, 1), d["fach_tiefe"] - 5, ti, "Oberseite Filz/Leder"),
        (platte, "Rückwand", 1, d["innen_l"] + 20, d["innen_h"] + 20, tr, "in Nut, verleimt (steift aus)"),
        (platte, "Sitzplatte", 1, po["sitz_laenge"], d["pad_b"], po["platte"], "Polsterträger"),
        (platte, "Lehnenplatte", 1, d["lehne_l"], d["pad_b"], po["platte"], "Polsterträger, Unterseite furniert"),
        (metall, "Gelenkplatte Korpus", 2, 90, 85, sb["gelenkplatte"], "gelasert, mit Fuß unter dem Sitz, 4 × M6 durch den Deckel"),
        (metall, "Gelenkplatte Lehne", 2, 110, 70, sb["gelenkplatte"], "gelasert, mit Lasche unter der Lehnenplatte"),
        (metall, "Stützenbein", 2, sb["stuetze_laenge"] + 30, sb["bein_breite"], sb["bein_dicke"], "Flachstahl, Bohrungen für Gelenk und Querstab"),
        (metall, "Querstab", 1, round(d["stab_l"]), sb["buegel_d"], sb["buegel_d"], "Rundstahl, mit den Beinen verschweißt"),
    ]


def ei(rects):
    """Verbundquerschnitt aus Rechtecken (Breite, Höhe, z-Unterkante, E) → EI und Schwerpunkt."""
    EA = sum(E * b * h for b, h, _, E in rects)
    zs = sum(E * b * h * (z0 + h / 2) for b, h, z0, E in rects) / EA
    EI = sum(E * (b * h ** 3 / 12 + b * h * (z0 + h / 2 - zs) ** 2) for b, h, z0, E in rects)
    return EI, zs


def statik(p, d, platz, F_last):
    m, last, sb, k = p["material"], p["last"], p["schraegbank"], p["korpus"]
    t, Em, Ep = d["t"], m["E_massiv"], m["E_platte"]
    F = last["nutzer_kg"] * G * last["dynamik"]
    res = []

    # 1. Vorderkante: Deckelstreifen + aufgeleimte Rastleiste (Rasten abgezogen).
    #    Die zwei Türnuten im Deckel werden mit negativem E abgezogen.
    nut_b = p["tueren"]["traverse_dicke"] + 1
    rects = [(100, t, 0, Em),
             (2 * nut_b, tu_nut(p), 0, -Em),
             (sb["leiste_breite"], p["polster"]["schattenfuge"] - sb["rast_tiefe"], t, Em)]
    EI, _ = ei(rects)
    l = d["fach_breite"] + d["ti"]
    w = 0.5 * F * l ** 3 / (48 * EI)
    res.append(("Vorderkante: Deckel + Rastleiste (50 % der Last)", 0.5 * F, l, w))

    # 2. Lehnenplatte flach auf den Rastleisten (Rippen nicht angesetzt)
    l2 = d["leiste_y0"][1] - d["leiste_y0"][0]
    I2 = 300 * p["polster"]["platte"] ** 3 / 12
    w2 = 5 * F * l2 ** 3 / (384 * Ep * I2)
    res.append(("Lehnenplatte flach zwischen den Rastleisten (Streifen 300 mm)", F, l2, w2))

    # 3. Lehne schräg: Kragarm hinter dem Stützengelenk, Platte + 2 Eichenrippen
    pp = p["polster"]["platte"]
    rects3 = [(d["pad_b"], pp, 0, Ep),
              (2 * sb["rippe_breite"], sb["rippe_hoehe"], -sb["rippe_hoehe"], Em)]
    EI3, _ = ei(rects3)
    a = d["lehne_l"] - sb["stuetze_abstand"]
    q = F_last * math.cos(math.radians(min(sb["winkel"]))) / d["lehne_l"]
    w3 = q * a ** 4 / (8 * EI3)
    res.append((f"Rückenlehne schräg, Überstand hinter der Stütze ({min(sb['winkel'])}°)", q * a, a, w3))

    # 4. Fachboden mit dem schwersten Inhalt der oberen Ebene
    if k["fachboden"]:
        for f in range(d["n_fach"]):
            kg = sum(i["kg"] for i in platz if i["fach"] == f and i["ebene"] == "oben")
            Ff = kg * G * 2
            l4 = d["fach_breite"]
            I4 = (d["fach_tiefe"] - 5) * d["ti"] ** 3 / 12
            w4 = 5 * Ff * l4 ** 3 / (384 * Ep * I4)
            res.append((f"Fachboden Fach {f + 1} ({fmt(kg)} kg × 2)", Ff, l4, w4))
    return res


def tu_nut(p):
    return p["tueren"]["nut_oben"]


def knicken(p, F_max):
    sb = p["schraegbank"]
    I = sb["bein_breite"] * sb["bein_dicke"] ** 3 / 12
    F_cr = math.pi ** 2 * E_STAHL * I / sb["stuetze_laenge"] ** 2
    return 2 * F_cr, 2 * F_cr / F_max


def gewicht(p, d):
    m, po, k, tu, sb = p["material"], p["polster"], p["korpus"], p["tueren"], p["schraegbank"]
    t, L, D = d["t"], d["L"], d["D"]
    sf = po["schattenfuge"]
    se, sh = k["sockel_einzug"], k["sockel_hoehe"]
    v_massiv = (2 * L * D * t + 2 * (d["korpus_h"] - 2 * t) * D * t
                + d["n_tuer"] * (d["n_lamellen"] * d["lamelle_b"] * d["tuer_h"] * tu["lamelle_dicke"]
                                 + 2 * d["tuer_l"] * 40 * tu["traverse_dicke"])
                + 2 * (d["leiste_x1"] - d["leiste_x0"]) * sb["leiste_breite"] * sf
                + 2 * d["rippe_l"] * sb["rippe_breite"] * sb["rippe_hoehe"]
                + 4 * (po["sitz_laenge"] - 50) * 20 * sf
                + 2 * (L - 2 * se) * sh * t + 2 * (D - 2 * se) * sh * t)
    v_platte = (d["n_mw"] * d["fach_tiefe"] * d["innen_h"] * d["ti"]
                + (d["n_fach"] if k["fachboden"] else 0) * d["fach_breite"] * d["fach_tiefe"] * d["ti"]
                + d["innen_l"] * d["innen_h"] * d["tr"]
                + (po["sitz_laenge"] + d["lehne_l"]) * d["pad_b"] * po["platte"])
    holz = v_massiv * 1e-9 * m["dichte_massiv"] + v_platte * 1e-9 * m["dichte_platte"]
    schaum = (po["sitz_laenge"] + d["lehne_l"]) * d["pad_b"] * po["schaum"] * 1e-9 * 45
    stahl = 7850e-9 * (4 * 90 * 85 * sb["gelenkplatte"]
                       + 2 * (sb["stuetze_laenge"] + 30) * sb["bein_breite"] * sb["bein_dicke"]
                       + d["stab_l"] * math.pi * (sb["buegel_d"] / 2) ** 2)
    rest = 1.5 + 1.5 + (0.4 if p["rollen"]["aktiv"] else 0)   # Leder, Beschläge, Rollen
    flaeche_massiv = (2 * L * D + 2 * d["korpus_h"] * D + d["n_tuer"] * d["tuer_l"] * d["tuer_h"]
                      + 2 * (L + D) * sh + (d["leiste_x1"] - d["leiste_x0"] + d["rippe_l"]) * 0.1) * 1e-6
    flaeche_platte = (d["n_mw"] * d["fach_tiefe"] * d["innen_h"] + d["n_fach"] * d["fach_breite"] * d["fach_tiefe"]
                      + (d["innen_l"] + 20) * (d["innen_h"] + 20)
                      + (po["sitz_laenge"] + d["lehne_l"]) * d["pad_b"]) * 1e-6
    return {"holz": holz, "schaum": schaum, "stahl": stahl, "rest": rest,
            "leer": holz + schaum + stahl + rest,
            "flaeche_massiv": flaeche_massiv, "flaeche_platte": flaeche_platte}


def ankippen(p, d):
    """Winkel und Hubhöhe, bis die verdeckten Rollen am rechten Ende greifen."""
    r, se = p["rollen"], p["korpus"]["sockel_einzug"]
    rad = r["durchmesser"] / 2
    dx, zc = se / 2, rad + r["bodenfreiheit"]
    a = 0.0
    while zc * math.cos(a) - dx * math.sin(a) > rad and a < math.radians(45):
        a += math.radians(0.1)
    return math.degrees(a), (d["L"] - se) * math.sin(a)


def fmt(x, n=1):
    return f"{x:,.{n}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def zahl(x):
    return fmt(x, 0 if float(x).is_integer() else 1)


def write_stueckliste(p, d, liste, platz, gw):
    m = p["material"]
    inhalt = sum(i["kg"] for i in platz)
    kosten_massiv = gw["flaeche_massiv"] * 1.25 * m["preis_massiv_m2"]
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
                out.append(f"| {name} | {n} | {zahl(l)} | {zahl(b)} | {zahl(dicke)} | {hinweis} |")
        out.append("")
    po = p["polster"]
    zug = 2 * (d["polster_h"] + 60)
    leder = ((po["sitz_laenge"] + zug) * (d["pad_b"] + zug) + (d["lehne_l"] + zug) * (d["pad_b"] + zug)) * 1e-6
    out += ["Maße in mm. Massivholz: Länge = Faserrichtung.", "",
            "## Polster", "",
            f"- Schaumstoff je Polster {po['schaum']} mm: 30 mm hart (RG 50+) unten, 20 mm mittel (RG 35–40) oben",
            "- Polyesterwatte 200 g/m² über den Schaum, damit die Kanten weich und voll wirken",
            f"- Bezug: ca. {fmt(leder, 2)} m² Leder (Vollnarben-Rindleder oder hochwertiges Kunstleder), mit Kedernaht an der Oberkante",
            "- Unterseite der Lehnenplatte: Furnier oder Leder, weil sie beim Aufstellen sichtbar ist", "",
            "## Beschläge und Kleinteile", "",
            "| Teil | Menge | Zweck |", "|---|---:|---|",
            "| Domino-/Lamello-Verbinder | ca. 40 | Gehrungen und Einbauten, verleimt |",
            "| Holzleim D3 | 1 | feuchtebeständig (Schweiß, Wischen) |",
            "| Gelenkbolzen M10 mit Messing- oder Gleitlagerbuchse, Hutmutter | 2 | Drehachse der Lehne |",
            "| Lagerböcke für die Stütze, Bolzen M8 | 2 | Gelenk der Stütze an den Rippen |",
            "| Gegenplatte Flachstahl 60 × 6 unter dem Deckel | 2 | nimmt die Zugkraft der Gelenkplatten auf |",
            "| Schrauben M6 durchgehend + Einschlagmuttern | 12 | Gelenkplatten und Sitz, lösbar |",
            f"| Bodenträger 5 mm | {4 * d['n_fach'] if p['korpus']['fachboden'] else 0} | Fachböden |",
            "| Gleitband für Laufnuten | 2,5 m | leiser Lauf der Schiebetüren |",
            f"| Rollen Ø {p['rollen']['durchmesser']} mm, gummiert, mit Platte | {2 if p['rollen']['aktiv'] else 0} | verdeckt am rechten Ende |",
            "| Antirutsch-Filzgleiter/Gummipads | 4 | unter dem Sockel |",
            "| Filz oder Leder 3 mm | ca. 0,5 m² | Auflage in den Hantelfächern |",
            f"| Abstandshalter Eiche | ca. {len([i for i in platz if i['typ'] == 'kh']) * 2} | zwischen den Hanteln, Fingerschutz |",
            "| Hartwachsöl (z. B. farblos oder „weiß“ gegen Nachdunkeln) | 0,75 l | Oberfläche |",
            "| Beize schwarz | 0,25 l | Sockel, Rastleisten, Distanzleisten |", "",
            "## Gewicht und Kosten (Schätzung)", "",
            f"- Holz {fmt(gw['holz'])} kg, Stahl {fmt(gw['stahl'])} kg, Schaum {fmt(gw['schaum'])} kg, Leder/Beschläge/Rollen {fmt(gw['rest'])} kg",
            f"- Bank leer: ca. **{fmt(gw['leer'])} kg**, mit Inventar ({fmt(inhalt)} kg): ca. **{fmt(gw['leer'] + inhalt)} kg**", "",
            "| Posten | Kosten |", "|---|---:|",
            f"| Eiche massiv, {fmt(gw['flaeche_massiv'], 2)} m² + 25 % Verschnitt à {m['preis_massiv_m2']} €/m² | ca. {fmt(kosten_massiv, 0)} € |",
            f"| Multiplex eichefurniert, {fmt(gw['flaeche_platte'], 2)} m² + 15 % à {m['preis_platte_m2']} €/m² | ca. {fmt(kosten_platte, 0)} € |",
            "| Leder, Schaum, Watte | 250–450 € |",
            "| Stahlteile gelasert, gekantet, pulverbeschichtet (oder Messing) | 120–250 € |",
            "| Beschläge, Rollen, Öl, Beize, Kleinteile | 100–150 € |",
            f"| **Material gesamt** | **ca. {fmt(holz_k + 470, 0)}–{fmt(holz_k + 850, 0)} €** |",
            "| optional: Polsterei für beide Polster | 250–450 € |", "",
            "Ohne Hanteln, Werkzeug und eigene Arbeitszeit. Preise sind grobe Annahmen und regional sehr verschieden.", ""]
    (ROOT / "docs" / "stueckliste.md").write_text("\n".join(out))
    return inhalt


def write_berechnung(p, d, platz, fehlt, belegt, gw, inhalt, rs, park, F_last, rfehler, rabst):
    sb, last, k, po = p["schraegbank"], p["last"], p["korpus"], p["polster"]

    def ok(w, g):
        return "✅" if w <= g else "⚠️"

    out = ["# Berechnung", "",
           "> Automatisch erzeugt aus `params.toml` mit `python3 tools/build.py`. Nicht von Hand ändern.",
           "> Überschlagsrechnung zur Plausibilisierung, kein Statik-Nachweis.", "",
           "## Hauptmaße", "",
           f"- Außen: {d['L']} × {d['D']} × {d['H']} mm (L × T × H), Sitz- = Trainingshöhe {d['H']} mm",
           f"- Polster {d['pad_b']} mm breit, rundum {po['einzug']} mm eingerückt, {po['schattenfuge']} mm Schattenfuge darunter",
           f"- Sitz {po['sitz_laenge']} mm + Fuge {po['fuge']} mm + Rückenlehne {d['lehne_l']} mm",
           f"- Korpus Eiche massiv {d['t']} mm auf Gehrung, Sockel {k['sockel_einzug']} mm zurückgesetzt",
           f"- Fächer: {d['n_fach']} × {fmt(d['fach_breite'])} mm breit, {d['fach_tiefe']} mm tief",
           f"- Schiebetüren: {d['n_tuer']} × {fmt(d['tuer_l'])} mm, je {d['n_lamellen']} Lamellen à {fmt(d['lamelle_b'])} mm", "",
           "## Schrägbank", "",
           f"Drehachse {sb['achse_unter_oberkante']} mm unter der Polsteroberfläche an der Vorderkante der Lehne "
           f"(x = {d['achse_x']} mm ab linkem Ende). Die Stütze ist {sb['stuetze_abstand']} mm hinter der Achse angelenkt, "
           f"{sb['stuetze_laenge']} mm lang und rastet in zwei Leisten auf dem Deckel ein.", "",
           f"Last: {int(sb['last_anteil'] * 100)} % von {last['nutzer_kg']} kg × {last['dynamik']} = {fmt(F_last, 0)} N "
           f"auf der Lehne, {sb['last_abstand']} mm hinter der Achse. Gerechnet sind zwei Lastfälle, "
           "das Gewicht senkrecht nach unten und die gleiche Last senkrecht auf die Lehnenfläche "
           "(kräftiges Zurücklehnen beim Drücken). Die Tabelle zeigt den ungünstigeren Fall.", "",
           "| Stellung | Rast ab Achse | Rast ab linkem Ende | Stützkraft | Achskraft | Neigung Stütze |",
           "|---|---:|---:|---:|---:|---:|",
           f"| 0° flach (Parkrast, {fmt(d['park_tiefe'], 0)} mm tief) | {fmt(park, 0)} mm | {fmt(d['achse_x'] + park, 0)} mm | – | – | 0° |"]
    for r in rs:
        if r["ok"]:
            out.append(f"| {r['winkel']}° | {fmt(r['n'], 0)} mm | {fmt(d['achse_x'] + r['n'], 0)} mm | "
                       f"{fmt(r['F'], 0)} N | {fmt(r['R'], 0)} N | {fmt(r['neigung'], 0)}° |")
        else:
            out.append(f"| {r['winkel']}° | – | – | – | – | Stütze zu kurz |")
    F_max = max((r["F"] for r in rs if r["ok"]), default=0)
    F_cr, sk = knicken(p, F_max)
    out += ["",
            f"- Rasttiefe {sb['rast_tiefe']} mm, kleinster Abstand zwischen zwei Rasten {fmt(rabst, 0)} mm "
            f"(Minimum {sb['min_rastabstand']} mm).",
            f"- Knicken der Stütze (2 × Flachstahl {sb['bein_breite']} × {sb['bein_dicke']}): "
            f"Knicklast {fmt(F_cr / 1000, 1)} kN bei max. {fmt(F_max / 1000, 2)} kN → Sicherheit ≈ {fmt(sk, 1)}.",
            f"- Die Achskraft verteilt sich auf zwei Bolzen M10: Scherspannung ≈ {fmt(max((r['R'] for r in rs if r['ok']), default=0) / 2 / (math.pi * 25), 0)} N/mm² (zulässig > 100 N/mm²).",
            "- Bei steiler Lehne zieht die Achse nach oben: Die Gelenkplatten werden mit durchgehenden Schrauben "
            "und einer Stahl-Gegenplatte unter dem Deckel befestigt, nicht nur mit Holzschrauben.",
            "- Kleinere Winkel als der kleinste Rastwinkel gehen mit einer einzigen Klappstütze nicht: "
            "Die Rast läge dann zu nah an der Parkrast.", ""]
    if rfehler:
        out += ["**⚠️ Geometrie prüfen:** " + "; ".join(rfehler), ""]
    else:
        out += ["✅ Alle Rasten liegen auf der Leiste und haben genug Abstand.", ""]

    out += ["## Stauraum-Belegung", "",
            "Schwerste Teile zuerst, untere Ebene zuerst.", "",
            "| Zelle | Inhalt | Breite | Höhe | Tiefe | kg |", "|---|---|---:|---:|---:|---:|"]
    for i in sorted(platz, key=lambda i: (i["fach"], i["ebene"] == "oben")):
        out.append(f"| {i['zelle']} | {i['name']} | {fmt(i['w'], 0)} | {fmt(i['h'], 0)} | {fmt(i['d'], 0)} | {fmt(i['kg'])} |")
    out += ["", "| Zelle | Zugangshöhe | belegt / verfügbar (Breite) |", "|---|---:|---:|"]
    for z in sorted(d["zellen"], key=lambda z: (z["fach"], z["ebene"] == "oben")):
        out.append(f"| {z['name']} | {fmt(z['zugang'], 0)} mm | {fmt(belegt[z['name']], 0)} / {fmt(z['breite'], 0)} mm |")
    out += ["", ("**⚠️ Passt nicht:** " + ", ".join(i["name"] for i in fehlt)) if fehlt
            else "✅ Alles Inventar findet Platz."]

    out += ["", "## Durchbiegung", "",
            f"Lastannahme: {last['nutzer_kg']} kg Nutzer × Stoßfaktor {last['dynamik']}.", "",
            "| Bauteil | Last | Stützweite | Durchbiegung | Grenze L/300 | |",
            "|---|---:|---:|---:|---:|---|"]
    for name, F, l, w in statik(p, d, platz, F_last):
        out.append(f"| {name} | {fmt(F, 0)} N | {fmt(l, 0)} mm | {fmt(w, 2)} mm | {fmt(l / 300, 2)} mm | {ok(w, l / 300)} |")
    out += ["", "Die verleimte Rückwand trägt die Hinterkante des Deckels zusätzlich mit. Sie ist hier nicht angesetzt.", ""]

    se, e = k["sockel_einzug"], po["einzug"]
    ueber = se - e
    out += ["## Kippsicherheit", "",
            f"Der Sockel steht {se} mm hinter der Korpuskante, das Polster {e} mm. "
            f"Eine Last am Polsterrand liegt also {ueber} mm außerhalb der Standfläche.", "",
            "| Fall | leer | mit Inventar |", "|---|---:|---:|"]
    seit = [gw["leer"] * (d["D"] / 2 - se) / ueber, (gw["leer"] + inhalt) * (d["D"] / 2 - se) / ueber]
    stirn = [gw["leer"] * (d["L"] / 2 - se) / ueber, (gw["leer"] + inhalt) * (d["L"] / 2 - se) / ueber]
    out.append(f"| Senkrechte Last auf der Längskante, ab der die Bank kippt | {fmt(seit[0], 0)} kg | {fmt(seit[1], 0)} kg |")
    out.append(f"| Senkrechte Last auf der Stirnkante, ab der die Bank kippt | {fmt(stirn[0], 0)} kg | {fmt(stirn[1], 0)} kg |")
    a_max = math.radians(max(sb["winkel"]))
    h_top = d["achse_z"] + d["lehne_l"] * math.sin(a_max)
    hebel = d["L"] - se - d["L"] / 2
    kipp = [(w * G * hebel / h_top) for w in (gw["leer"], gw["leer"] + inhalt)]
    out.append(f"| Lehne {max(sb['winkel'])}°: waagerechter Zug/Druck nach hinten an der Lehnenoberkante ({fmt(h_top, 0)} mm hoch), niemand sitzt | "
               f"{fmt(kipp[0], 0)} N | {fmt(kipp[1], 0)} N |")
    mit_person = kipp[0] + last["nutzer_kg"] * G * (d["L"] - se - (d["sitz_x0"] + d["sitz_x1"]) / 2) / h_top
    out += ["",
            f"Sitzt jemand auf dem Sitz, steigt der letzte Wert (leere Bank) auf ≈ {fmt(mit_person, 0)} N. "
            "Beim Training ist das unkritisch. Die aufgestellte Lehne ist aber kein Griff zum Hochziehen, "
            "wenn die Bank leer ist.", ""]
    if p["rollen"]["aktiv"]:
        a, hub = ankippen(p, d)
        out += ["## Transport", "",
                f"- Die Rollen sitzen verdeckt unter dem Korpusüberstand am rechten Ende und greifen ab ≈ {fmt(a)}° Neigung.",
                f"- Dazu das linke Ende unter dem Überstand fassen und ≈ {fmt(hub, 0)} mm anheben.",
                f"- Dabei zu heben (halbes Gewicht): leer ≈ {fmt(gw['leer'] / 2, 0)} kg, mit Inventar ≈ {fmt((gw['leer'] + inhalt) / 2, 0)} kg "
                "→ schwere Hanteln vorher herausnehmen.", ""]
    (ROOT / "docs" / "berechnung.md").write_text("\n".join(out))


ANSICHTEN = [
    # Datei, Kamera (tx,ty,tz,rx,ry,rz,dist), Projektion, -D Optionen
    ("moebel.png", "600,200,230,70,0,25,2500", "p", {}),
    ("moebel_nussbaum.png", "600,200,230,70,0,25,2500", "p", {"farbschema": '"nussbaum"'}),
    ("schraeg.png", "600,200,450,70,0,25,3400", "p", {"lehne_winkel": "45"}),
    ("verstellung.png", "640,0,700,90,0,0,3000", "o", {"lehne_winkel": "45", "geist": "true", "zeige_inhalt": "false"}),
    ("stauraum.png", "600,200,230,70,0,25,2500", "p", {"zeige_tueren": "false"}),
    ("explosion.png", "600,200,300,66,0,25,3400", "p", {"explosion": "1"}),
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
    rs, park, F_last = rasten(p, d)
    rfehler, rabst = pruefe_rasten(p, d, rs, park)
    platz, fehlt, belegt = pack(p, d)
    write_scad(p, d, platz, rs, park)
    gw = gewicht(p, d)
    inhalt = write_stueckliste(p, d, teile(p, d), platz, gw)
    write_berechnung(p, d, platz, fehlt, belegt, gw, inhalt, rs, park, F_last, rfehler, rabst)
    print("cad/params.scad, docs/stueckliste.md, docs/berechnung.md geschrieben")
    for w in rfehler:
        print("WARNUNG Schrägbank:", w)
    if fehlt:
        print("WARNUNG – passt nicht in den Stauraum:", ", ".join(i["name"] for i in fehlt))
    if "--no-render" not in sys.argv:
        render()


if __name__ == "__main__":
    main()
