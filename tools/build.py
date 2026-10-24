#!/usr/bin/env python3
"""Erzeugt aus params.toml alle abgeleiteten Dateien der Bank.

- cad/params.scad       Parameter + abgeleitete Maße für das OpenSCAD-Modell
- docs/stueckliste.md   Planungsstückliste nach Gewerken, Gewicht, grobe Kosten
- docs/berechnung.md    Gleitstützen von Lehne und Sitz, Polsterfuge, Stauraum, Rahmen, Kippsicherheit, Fahrwerk
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
    b, m, po, me, k, rt, ra = (p["bank"], p["material"], p["polster"], p["mechanik"],
                               p["korpus"], p["rolltuer"], p["rahmen"])
    L, D, H, R = b["laenge"], b["tiefe"], b["hoehe"], b["eckradius"]
    t, ti = m["aussen"], m["innen"]
    d = {"L": L, "D": D, "H": H, "R": R, "t": t, "ti": ti}

    # Höhenaufbau: Polster → Wanne (Rand) → Wannenboden → Innenraum → Boden → Sockel
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
    d["pad_y0"] = t + po["luft_seite"]
    d["pad_b"] = D - 2 * d["pad_y0"]
    d["pad_r_aussen"] = max(po["radius"], R - t - po["luft_seite"])
    d["lehne_x0"] = t + po["luft_ende"]
    d["sitz_x1"] = L - d["lehne_x0"]
    d["sitz_x0"] = d["sitz_x1"] - po["sitz_laenge"]
    d["lehne_x1"] = d["sitz_x0"] - po["fuge"]
    d["lehne_l"] = d["lehne_x1"] - d["lehne_x0"]

    # Rolltür vorn zwischen den Eckrundungen; offen in der Tasche links und hinter dem Nutzraum
    d["rt_x0"], d["rt_x1"] = R, L - R
    d["rt_len"] = d["rt_x1"] - d["rt_x0"]
    d["rt_y0"] = rt["luft"]
    n = round((d["rt_len"] + rt["lamelle_fuge"]) / (rt["lamelle_breite"] + rt["lamelle_fuge"]))
    d["rt_n"] = n
    d["rt_b"] = (d["rt_len"] - (n - 1) * rt["lamelle_fuge"]) / n
    d["rt_lamelle_l"] = d["innen_h"] + 2 * rt["nut"] - 2
    d["fach_y0"] = t + 3
    d["rt_hinten_y0"] = D - t - rt["luft"] - rt["lamelle_dicke"]
    d["fach_y1"] = d["rt_hinten_y0"] - 3
    d["fach_tiefe"] = d["fach_y1"] - d["fach_y0"]
    d["rt_speicher"] = d["fach_tiefe"] + (d["innen_l"] - k["tasche"]) - 2 * rt["biegeradius"]

    # Tasche, Hantelbereich, Zubehörbereich
    d["tasche_x0"], d["tasche_x1"] = t, t + k["tasche"]
    breiten = list(k["faecher"])
    rest = d["innen_l"] - k["tasche"] - ti - sum(breiten) - len(breiten) * ti
    breiten.append(rest)
    d["fach_breiten"] = breiten
    x = d["tasche_x1"]
    d["mw_x"], d["fach_x0"] = [], []
    for bb in breiten:
        d["mw_x"].append(x)
        x += ti
        d["fach_x0"].append(x)
        x += bb
    d["n_fach"] = len(breiten)
    d["n_mw"] = len(d["mw_x"])
    d["ebene_z0"] = d["boden_z1"] + k["fach_unten"]          # Traverse bzw. Fachboden der oberen Ebene
    d["ebene_z1"] = d["ebene_z0"] + ti
    zellen = []
    for i, (x0, bb) in enumerate(zip(d["fach_x0"], breiten)):
        offen = min(x0 + bb, d["rt_x1"]) - max(x0, d["rt_x0"])
        for ebene, z0, z1 in (("unten", d["boden_z1"], d["ebene_z0"]), ("oben", d["ebene_z1"], d["deckel_z0"])):
            zellen.append({"name": f"{'Hantelbereich' if i == 0 else 'Zubehör'} {ebene}", "fach": i, "ebene": ebene,
                           "x0": x0, "z0": z0, "h": z1 - z0, "zugang": z1 - z0,
                           "breite": bb, "offen": offen, "tiefe": d["fach_tiefe"]})
    zellen.sort(key=lambda z: (z["ebene"] == "oben", z["fach"]))
    d["zellen"] = zellen

    # Innenrahmen: Längsrohre in der Wanne, Stützen bis zu den Füßen, Traversen für die Hanteln
    st = ra["stuetze"]
    d["rohr_y0"] = [t + 3, D - t - 3 - ra["rohr_b"]]
    d["stuetze_x"] = [d["mw_x"][0] + ti + 2, d["mw_x"][1] - st - 2, L - t - 3 - st]
    # Stützen innerhalb der Sockelzarge (sonst sähe man sie im Sockelrücksprung)
    zarge_innen = k["sockel_einzug"] + 20
    d["stuetze_y"] = [zarge_innen + 2, D - zarge_innen - 2 - st]
    d["fuss_pos"] = [[x + st / 2, y + st / 2] for y in d["stuetze_y"] for x in (d["stuetze_x"][0], d["stuetze_x"][-1])]
    d["traverse_y"] = None                                    # nach den Hanteln gesetzt (pack)

    # Fahrwerk
    d["rollen_pos"] = [[x + st / 2 + (60 if i == 0 else -60), y]
                       for y in (d["stuetze_y"][0] + st + 40, d["stuetze_y"][1] - 40)
                       for i, x in enumerate((d["stuetze_x"][0], d["stuetze_x"][-1]))]
    d["pedal_x"] = L - 150

    # Mechanik: gemeinsame Werte
    e = me["achse_unter_oberkante"]
    d["achse_z"] = H - e
    d["vA"] = -(P - e) - me["stuetze_versatz"]
    d["schiene_z"] = d["deckel_z1"] + me["schiene_h"] / 2 - d["achse_z"]   # Bolzenmitte relativ zur Achse
    d["bein_y0"] = [d["rohr_y0"][0] + ra["rohr_b"] + 8, d["rohr_y0"][1] - 8 - me["bein_breite"]]
    d["stab_y0"] = d["bein_y0"][0]
    d["stab_l"] = d["bein_y0"][1] + me["bein_breite"] - d["bein_y0"][0]
    rippe_y = d["bein_y0"][0] + me["bein_breite"] + 25
    d["rippe_y0"] = [rippe_y, D - rippe_y - me["rippe_breite"]]

    # Lehne und Sitz drehen um eine gemeinsame Achse in der Mitte der Fuge
    d["achse_x"] = d["lehne_x1"] + po["fuge"] / 2
    d["achs_versatz"] = po["fuge"] / 2
    d["teile"] = {}
    for teil, richtung, laenge in (("lehne", -1, d["lehne_l"]), ("sitz", 1, po["sitz_laenge"])):
        q = p[teil]
        achse = d["achse_x"]
        c = d["achs_versatz"]
        tl = {"teil": teil, "achse_x": achse, "dir": richtung, "laenge": laenge, "winkel": q["winkel"],
              "s": q["stuetze_abstand"], "l": q["stuetze_laenge"], "u0": c + 40, "u1": c + laenge - 10}
        xa, xb = achse + richtung * tl["u0"], achse + richtung * tl["u1"]
        tl["schiene_x0"], tl["schiene_x1"] = min(xa, xb), max(xa, xb)
        tl["rippe_l"] = min(tl["s"] + 40, laenge - 30) if teil == "lehne" else 0
        d["teile"][teil] = tl
    return d


def gx(tl, u):
    """Lokale Lage auf einem Klappteil (ab Drehachse) → x ab linkem Ende."""
    return tl["achse_x"] + tl["dir"] * u


def rasten(p, d, teil, s=None, l=None):
    """Lochpositionen der Gleitschiene je Winkel (0° = flach), Stützkraft, Achskraft."""
    tl, q, me, last = d["teile"][teil], p[teil], p["mechanik"], p["last"]
    s = s or tl["s"]
    l = l or tl["l"]
    vA, zN = d["vA"], d["schiene_z"]
    F_last = q["last_anteil"] * last["nutzer_kg"] * G * last["dynamik"]
    out = []
    for a in [0] + list(tl["winkel"]):
        r = math.radians(a)
        Ax = s * math.cos(r) - vA * math.sin(r)
        Az = s * math.sin(r) + vA * math.cos(r)
        dz = Az - zN
        if abs(dz) >= l:
            out.append({"winkel": a, "ok": False})
            continue
        n = Ax + math.sqrt(l * l - dz * dz)
        ux, uz = (Ax - n) / l, dz / l             # Richtung Fuß → Gelenk (Druckstab)
        hebel = Ax * uz - Az * ux
        F, R = 0.0, 0.0
        if a > 0:
            lastfaelle = [
                ((0.0, -F_last), F_last * (q["last_abstand"] * math.cos(r) - me["achse_unter_oberkante"] * math.sin(r))),
                ((F_last * math.sin(r), -F_last * math.cos(r)), F_last * q["last_abstand"]),
            ]
            for (Lx, Lz), M in lastfaelle:
                Fi = M / hebel
                F = max(F, Fi)
                R = max(R, math.hypot(-Fi * ux - Lx, -Fi * uz - Lz))
        out.append({"winkel": a, "ok": True, "n": n, "F": F, "R": R,
                    "neigung": math.degrees(math.atan2(uz, -ux))})
    return out, F_last


def pruefe_rasten(p, d, teil, rs):
    """Rastlöcher für die Arbeitswinkel; flach steht der Gleitschuh am Endanschlag (Kugelschnäpper)."""
    tl, me = d["teile"][teil], p["mechanik"]
    fehler = [f"{r['winkel']}°: Stütze erreicht die Schiene nicht" for r in rs if not r["ok"]]
    pos = sorted(r["n"] for r in rs if r["ok"] and r["winkel"] > 0)
    anschlag = max((r["n"] for r in rs if r["ok"] and r["winkel"] == 0), default=0)
    lo, hi = tl["u0"] + 10, tl["u1"] - 10
    if anschlag > hi:
        fehler.append(f"Endanschlag (flach) bei {fmt(anschlag, 0)} mm liegt außerhalb der Schiene")
    if pos and (pos[0] < lo or pos[-1] > hi):
        fehler.append(f"Löcher außerhalb der Schiene ({fmt(pos[0], 0)}–{fmt(pos[-1], 0)} mm, erlaubt {fmt(lo, 0)}–{fmt(hi, 0)} mm)")
    abst = min((b_ - a_ for a_, b_ in zip(pos, pos[1:])), default=999)
    if abst < me["loch_abstand_min"]:
        fehler.append(f"Löcher zu dicht ({fmt(abst, 0)} mm < {me['loch_abstand_min']} mm)")
    return fehler, abst


def suche_stuetze(p, d):
    """Sucht je Klappteil Anlenkpunkt und Länge der Stütze mit kleinster Stützkraft."""
    for teil in TEILE:
        tl = d["teile"][teil]
        treffer = []
        for s in range(60, int(tl["laenge"]), 10):
            for l in range(60, int(tl["laenge"]), 10):
                rs, _ = rasten(p, d, teil, s, l)
                if not pruefe_rasten(p, d, teil, rs)[0]:
                    treffer.append((max(r["F"] for r in rs), s, l))
        treffer.sort()
        print(f"[{teil}] Winkel {tl['winkel']}, Länge {tl['laenge']} mm – beste Stützen (max. Stützkraft, Abstand, Länge):")
        for F, s, l in treffer[:6]:
            print(f"  {F:6.0f} N   stuetze_abstand = {s}   stuetze_laenge = {l}")
        if not treffer:
            print("  keine Lösung – Winkel oder Länge ändern")


def kante(p, d, a):
    """Abstand der gerundeten Polster-Innenkante von der gemeinsamen Achse (waagerecht), angestellt um a°.
    Die Kante beginnt c = Fuge/2 neben der Achse; die Rundung (Radius r) liegt e − r über der Achse."""
    e, r = p["mechanik"]["achse_unter_oberkante"], p["polster"]["radius"]
    c, w = d["achs_versatz"], math.radians(a)
    rundung = (c + r) * math.cos(w) - (e - r) * math.sin(w) - r
    flanke = c * math.cos(w) - (e - r) * math.sin(w) if e > r else c * math.cos(w)
    return min(rundung, flanke)


def fuge_pruefen(p, d):
    """Kleinster Abstand der Polsterkanten über alle Stellungskombinationen."""
    kombis = []
    for al in [0] + d["teile"]["lehne"]["winkel"]:
        for as_ in [0] + d["teile"]["sitz"]["winkel"]:
            kombis.append((kante(p, d, al) + kante(p, d, as_), al, as_))
    return min(kombis)


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
        lk = m_kopf / (A * rs_) + math.pi * D * fa ** 2 / A
        out.append({"kg": kg, "D": D, "lk": lk, "laenge": gl + 2 * lk, "m_kopf": m_kopf,
                    "kern_l": gl + 2 * h["gewinde_tiefe"], "liegehoehe": D - ab})
    return out, m_griff


def pack(p, d, hs):
    """Hanteln einzeln in Aufnahmen (nur Hantelbereich), Zubehör im Zubehörbereich; schwer zuerst, unten zuerst."""
    gap = p["inventar"]["abstand"]
    k = p["korpus"]
    items = []
    for x in hs:
        for nr in (1, 2):
            items.append({"name": f"Kurzhantel {fmt(x['kg'])} kg ({nr})", "typ": "khr", "kg": x["kg"],
                          "w": x["D"] + k["halter_anschlag"], "h": x["D"] + k["halter_luft"], "d": x["laenge"],
                          "kopf": x["D"], "kopf_l": x["lk"], "nur_fach": 0})
    for it in p.get("inhalt", []):
        items.append({**it, "w": it["breite"], "h": it["hoehe"], "d": it["tiefe"], "nur_fach": 1})
    items.sort(key=lambda i: -i["kg"])

    # Die Rahmenstützen stehen vorn und hinten in den Fächern. Hanteln (Aufnahmen auf den Traversen
    # zwischen den Stützen) und Teile, die in der Tiefe an die Stützen reichen, liegen neben ihnen.
    st = p["rahmen"]["stuetze"]
    frei_y = (d["stuetze_y"][0] + st, d["stuetze_y"][1])
    stuetzen = [(x, x + st) for x in d["stuetze_x"]]

    def stelle(z, w, tief, hantel):
        x = z["x0"] + belegt[z["name"]]
        y = d["fach_y0"] + (z["tiefe"] - tief) / 2
        if hantel or y < frei_y[0] or y + tief > frei_y[1]:
            for s0, s1 in stuetzen:
                if x < s1 + gap and x + w + gap > s0:
                    x = s1 + gap
        return x, y

    belegt = {z["name"]: gap for z in d["zellen"]}
    platz, fehlt = [], []
    for it in items:
        lagen = [(it["w"], it["d"])]
        if it["typ"] == "box" and it["w"] != it["d"]:
            lagen.append((it["d"], it["w"]))            # Zubehör darf gedreht liegen
        for z, (w, tief) in ((z, l) for z in d["zellen"] for l in lagen):
            if z["fach"] != it["nur_fach"] or it["h"] + 10 > z["zugang"] or tief > z["tiefe"]:
                continue
            x, y = stelle(z, w, tief, it["typ"] == "khr")
            if x + w + gap <= z["x0"] + z["breite"]:
                platz.append({**it, "w": w, "d": tief, "zelle": z["name"], "fach": z["fach"],
                              "ebene": z["ebene"], "x": x, "y": y, "z": z["z0"]})
                belegt[z["name"]] = x + w + gap - z["x0"]
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
    k, rt, ro, po, me, ra = p["korpus"], p["rolltuer"], p["rollen"], p["polster"], p["mechanik"], p["rahmen"]
    werte = {k_: d[k_] for k_ in (
        "L", "D", "H", "R", "t", "ti", "polster_h", "polster_z0", "rand_top", "deckel_z0", "deckel_z1",
        "boden_z0", "boden_z1", "korpus_h", "innen_l", "innen_h",
        "pad_y0", "pad_b", "pad_r_aussen", "lehne_x0", "lehne_x1", "lehne_l", "sitz_x0", "sitz_x1",
        "rt_x0", "rt_x1", "rt_len", "rt_y0", "rt_n", "rt_b", "rt_hinten_y0",
        "fach_y0", "fach_y1", "fach_tiefe", "tasche_x0", "tasche_x1", "mw_x", "fach_x0", "fach_breiten",
        "ebene_z0", "ebene_z1", "rohr_y0", "stuetze_x", "stuetze_y", "fuss_pos", "rollen_pos", "pedal_x",
        "achse_z", "vA", "schiene_z", "bein_y0", "stab_y0", "stab_l", "rippe_y0", "achs_versatz")}
    werte.update({
        "polster_platte": po["platte"], "polster_r": po["radius"], "rand": po["rand"],
        "sockel_h": k["sockel_hoehe"], "sockel_einzug": k["sockel_einzug"],
        "fuss_d": k["fuss_d"], "fuss_h": k["fuss_h"], "halter_luft": k["halter_luft"],
        "rt_fuge": rt["lamelle_fuge"], "rt_dicke": rt["lamelle_dicke"],
        "bein_b": me["bein_breite"], "bein_t": me["bein_dicke"], "bolzen_d": me["bolzen_d"],
        "schiene_h": me["schiene_h"], "schiene_b": me["schiene_b"],
        "rippe_b": me["rippe_breite"], "rippe_h": me["rippe_hoehe"], "gelenkplatte": me["gelenkplatte"], "konsole_b": me["konsole_breite"],
        "rohr_b": ra["rohr_b"], "rohr_h": ra["rohr_h"], "stuetze_q": ra["stuetze"],
        "traverse_b": ra["traverse_b"], "traverse_t": ra["traverse_t"],
        "rolle_d": ro["durchmesser"],
        # [typ, x, y, z, breite, hoehe, tiefe, kopf, kopflänge]
        "inhalt": [[i["typ"], i["x"], i["y"], i["z"], i["w"], i["h"], i["d"], i.get("kopf", 0), i.get("kopf_l", 0)]
                   for i in platz],
        "abflachung": p["hanteln"]["abflachung"], "griff_d": p["hanteln"]["griff_d"],
    })
    for teil in TEILE:
        tl = d["teile"][teil]
        rs, _ = rast[teil]
        werte.update({f"{teil}_achse_x": tl["achse_x"], f"{teil}_dir": tl["dir"], f"{teil}_laenge": tl["laenge"],
                      f"{teil}_s": tl["s"], f"{teil}_l_stuetze": tl["l"], f"{teil}_winkel_liste": tl["winkel"],
                      f"{teil}_loecher": [r_["n"] for r_ in rs if r_["ok"] and r_["winkel"] > 0],
                      f"{teil}_anschlag": max(r_["n"] for r_ in rs if r_["winkel"] == 0),
                      f"{teil}_schiene_x0": tl["schiene_x0"], f"{teil}_schiene_x1": tl["schiene_x1"],
                      f"{teil}_rippe_l": tl["rippe_l"]})
    lines = ["// AUTOMATISCH ERZEUGT von tools/build.py aus params.toml – nicht von Hand ändern.", ""]
    lines += [f"{k_} = {scad_value(v)};" for k_, v in werte.items()]
    (ROOT / "cad" / "params.scad").write_text("\n".join(lines) + "\n")


def teile(p, d, platz):
    """Planungsstückliste: (Gewerk, Bezeichnung, Anzahl, Länge, Breite, Dicke, Hinweis)."""
    t, ti, R, L, D = d["t"], d["ti"], d["R"], d["L"], d["D"]
    k, rt, po, me, ra, ro = p["korpus"], p["rolltuer"], p["polster"], p["mechanik"], p["rahmen"], p["rollen"]
    se, sh, fh = k["sockel_einzug"], k["sockel_hoehe"], k["fuss_h"]
    lb, st = d["teile"]["lehne"], d["teile"]["sitz"]
    holz, metall, fahr = "Holzbau (Schreiner)", "Metallbau und Beschläge", "Fahrwerk"
    n_hantel = len([i for i in platz if i["typ"] == "khr"])
    rohr_l = L - 2 * t - 6
    st_h = d["rand_top"] - k["fuss_h"] - ra["rohr_h"]
    return [
        (holz, "Wannenboden (Deckel)", 1, L - 2 * t, D - 2 * t, t, f"furniert, Ecken R {R - t}, Laufnut Rolltür {rt['nut']} × {rt['nut']}, Durchbrüche für die Rahmenstützen"),
        (holz, "Boden", 1, L - 2 * t, D - 2 * t, t, f"furniert, Ecken R {R - t}, Laufnut Rolltür, Durchbrüche für die Stützen"),
        (holz, "Stirnseite", 2, d["korpus_h"], D - 2 * R, t, "furniert, Furnier stehend"),
        (holz, "Eckrundung", 4, d["korpus_h"], R, R, f"formverleimt oder massiv, außen R {R}, Furnier stehend"),
        (holz, "Rückwand", 1, L - 2 * R, d["korpus_h"], t, "furniert stehend, Sichtseite zum Bett, Wartungsöffnung vorsehen"),
        (holz, "Frontleiste oben", 1, L - 2 * R, po["rand"] + t, t, "massiv Eiche, bildet vorn den Rand, Laufnut unten"),
        (holz, "Frontleiste unten", 1, L - 2 * R, t, t, "massiv Eiche, Laufnut oben"),
        (holz, "Rolltür-Lamelle", d["rt_n"], d["rt_lamelle_l"], round(d["rt_b"], 1), rt["lamelle_dicke"],
         f"Eiche massiv, Vorderseite gerundet, auf flexiblem Träger, Fuge {fmt(rt['lamelle_fuge'])}"),
        (holz, "Trennwand", d["n_mw"], d["fach_tiefe"], d["innen_h"], ti, "nicht tragend, endet vor dem Rücklaufkanal"),
        (holz, "Fachboden Zubehör", 1, round(d["fach_breiten"][-1] - 2), d["fach_tiefe"] - 5, ti, "auf Bodenträgern, Ausklinkungen für die Rahmenstützen"),
        (holz, "Lehnenplatte", 1, lb["laenge"], d["pad_b"], po["platte"], f"Multiplex, Eichenkante, Ecken außen R {d['pad_r_aussen']}, 2 Rippen 60 × 18"),
        (holz, "Sitzplatte", 1, st["laenge"], d["pad_b"], po["platte"], f"Multiplex, Eichenkante, Ecken außen R {d['pad_r_aussen']}"),
        (holz, "Sockelzarge", 1, round(rr_umfang(L - 2 * se, D - 2 * se, R - se)), sh - fh, 20, f"umlaufend, Ecken R {R - se}, Pedalausschnitt vorn rechts, Abwicklung"),
        (metall, "Längsrohr Innenrahmen", 2, rohr_l, ra["rohr_b"], ra["rohr_h"], f"Rechteckrohr {ra['rohr_b']} × {ra['rohr_h']} × {ra['rohr_t']}, liegt in der Wanne, trägt Polster und Gelenke"),
        (metall, "Stütze Innenrahmen", 2 * len(d["stuetze_x"]), round(st_h), ra["stuetze"], ra["stuetze"], f"Vierkantrohr {ra['stuetze']} × {ra['stuetze']} × 2, unten mit Gewinde für die Füße"),
        (metall, "Querrohr Innenrahmen", 2 * len(d["stuetze_x"]), round(d["stuetze_y"][1] - d["stuetze_y"][0] + ra["stuetze"]), ra["stuetze"], ra["stuetze"], "oben und unten zwischen den Stützen"),
        (metall, "Hantel-Traverse", 4, round(d["fach_breiten"][0]), ra["traverse_b"], ra["traverse_t"], "Flachstahl hochkant, zwischen den Stützen, je Ebene 2"),
        (metall, "Hantelaufnahme", n_hantel, 0, 0, 0, "2 gepolsterte Auflagen am Griff, seitliche Anschläge, lösbarer Sicherungsbügel"),
        (metall, "Gelenkkonsole", 2, round(d["achse_z"] - d["deckel_z1"] - ra["rohr_h"] + 10), me["konsole_breite"], me["gelenkplatte"], "auf die Längsrohre geschweißt, gemeinsame Achse M10 für Lehne und Sitz"),
        (metall, "Gelenklasche Lehne / Sitz", 4, 110, 70, me["gelenkplatte"], "unter die Polsterplatte geschraubt, auf derselben Achse mit Gleitlagern"),
        (metall, "Gleitstütze Lehne", 1, lb["l"], round(d["stab_l"]), me["bein_dicke"], f"2 Beine {me['bein_breite']} × {me['bein_dicke']}, Steg, 2 Gleitschuhe mit Indexbolzen Ø {me['bolzen_d']}"),
        (metall, "Gleitstütze Sitz", 1, st["l"], round(d["stab_l"]), me["bein_dicke"], f"2 Beine {me['bein_breite']} × {me['bein_dicke']}, Steg, 2 Gleitschuhe mit Indexbolzen Ø {me['bolzen_d']}"),
        (metall, "Gleitschiene Lehne", 2, round(lb["schiene_x1"] - lb["schiene_x0"]), me["schiene_b"], me["schiene_h"], f"C-Profil mit {len(lb['winkel']) + 1} Rastlöchern, auf Querrohren"),
        (metall, "Gleitschiene Sitz", 2, round(st["schiene_x1"] - st["schiene_x0"]), me["schiene_b"], me["schiene_h"], f"C-Profil mit {len(st['winkel']) + 1} Rastlöchern"),
        (metall, "Indexbolzen mit Zugknopf", 4, me["bolzen_d"], 0, 0, "federnd, rastet selbsttätig, formschlüssig"),
        (fahr, "Rollenrahmen", 1, round(d["rollen_pos"][1][0] - d["rollen_pos"][0][0] + 60), round(d["rollen_pos"][2][1] - d["rollen_pos"][0][1] + 60), 20, "Stahlrahmen, in den Stützen geführt"),
        (fahr, "Lenkrolle", ro["anzahl"], ro["durchmesser"], 0, 0, "gummiert, parkettgeeignet, mit Feststeller"),
        (fahr, "Exzenterwelle", 2, round(d["stuetze_y"][1] - d["stuetze_y"][0]), 20, 20, "quer, über Koppelstange verbunden"),
        (fahr, "Fußpedal (Bronze)", 1, 90, 30, 6, "versenkt im Sockel rechts, Totpunktrast in beiden Lagen"),
        (fahr, "Stellfuß", 4, k["fuss_d"], k["fuss_h"], 0, "an den Eckstützen, höhenverstellbar, Filz"),
    ]


def rohr_I(b, h, w):
    return (b * h ** 3 - (b - 2 * w) * (h - 2 * w) ** 3) / 12


def statik(p, d, platz, rast):
    m, last, me, k, po, ra = p["material"], p["last"], p["mechanik"], p["korpus"], p["polster"], p["rahmen"]
    Es, Ep = m["E_stahl"], m["E_platte"]
    F = last["nutzer_kg"] * G * last["dynamik"]
    res = []
    # 1. Längsrohr des Innenrahmens zwischen zwei Stützen, halbe Last in Feldmitte
    sx = d["stuetze_x"]
    l = max(b_ - a_ for a_, b_ in zip(sx, sx[1:]))
    I = rohr_I(ra["rohr_b"], ra["rohr_h"], ra["rohr_t"])
    res.append((f"Längsrohr {ra['rohr_b']} × {ra['rohr_h']} × {ra['rohr_t']} (50 % der Last)", 0.5 * F, l,
                0.5 * F * l ** 3 / (48 * Es * I)))
    # 2. Polsterplatte zwischen den Längsrohren
    l2 = d["rohr_y0"][1] - (d["rohr_y0"][0] + ra["rohr_b"])
    I2 = 300 * po["platte"] ** 3 / 12
    res.append(("Polsterplatte zwischen den Längsrohren (Streifen 300 mm)", F, l2, 5 * F * l2 ** 3 / (384 * Ep * I2)))
    # 3. Klappteile angestellt: Überstand hinter dem Stützengelenk
    for teil in TEILE:
        tl = d["teile"][teil]
        F_last = rast[teil][1]
        a = d["achs_versatz"] + tl["laenge"] - tl["s"]
        if a <= 0:
            continue
        rects = [(d["pad_b"], po["platte"], 0, Ep)]
        if teil == "lehne":
            rects.append((2 * me["rippe_breite"], me["rippe_hoehe"], -me["rippe_hoehe"], 11000))
        EA = sum(E * b * h for b, h, _, E in rects)
        zs = sum(E * b * h * (z0 + h / 2) for b, h, z0, E in rects) / EA
        EI = sum(E * (b * h ** 3 / 12 + b * h * (z0 + h / 2 - zs) ** 2) for b, h, z0, E in rects)
        q = F_last * math.cos(math.radians(min(tl["winkel"]))) / tl["laenge"]
        res.append((f"{NAME[teil]} angestellt, Überstand hinter der Stütze", q * a, a, q * a ** 4 / (8 * EI)))
    # 4. Hantel-Traverse der oberen Ebene (2 Stück), Flachstahl hochkant
    kg = sum(i["kg"] for i in platz if i["fach"] == 0 and i["ebene"] == "oben")
    Ft = kg * G * 2 / 2
    lt = d["fach_breiten"][0]
    It = ra["traverse_t"] * ra["traverse_b"] ** 3 / 12
    res.append((f"Hantel-Traverse obere Ebene ({fmt(kg)} kg × 2, je Traverse)", Ft, lt, 5 * Ft * lt ** 3 / (384 * Es * It)))
    return res


def knicken(p, d, teil, F_max):
    me = p["mechanik"]
    I = me["bein_breite"] * me["bein_dicke"] ** 3 / 12
    F_cr = 2 * math.pi ** 2 * p["material"]["E_stahl"] * I / d["teile"][teil]["l"] ** 2
    return F_cr, F_cr / F_max if F_max else 99


def gewicht(p, d, platz):
    m, po, k, rt, me, ra = p["material"], p["polster"], p["korpus"], p["rolltuer"], p["mechanik"], p["rahmen"]
    t, L, D, R = d["t"], d["L"], d["D"], d["R"]
    se, sh, fh = k["sockel_einzug"], k["sockel_hoehe"], k["fuss_h"]
    lb, st = d["teile"]["lehne"], d["teile"]["sitz"]
    mantel = rr_umfang(L, D, R) * d["korpus_h"] - d["rt_len"] * d["innen_h"]
    platten = 2 * rr_flaeche(L - 2 * t, D - 2 * t, R - t)
    innen = d["n_mw"] * d["fach_tiefe"] * d["innen_h"] + d["fach_breiten"][-1] * d["fach_tiefe"]
    v_platte = (mantel + platten) * t + innen * d["ti"] + (lb["laenge"] + st["laenge"]) * d["pad_b"] * po["platte"]
    v_massiv = (d["rt_n"] * d["rt_b"] * d["rt_lamelle_l"] * rt["lamelle_dicke"]
                + rr_umfang(L - 2 * se, D - 2 * se, R - se) * 20 * (sh - fh)
                + 2 * lb["rippe_l"] * me["rippe_breite"] * me["rippe_hoehe"])
    holz = v_platte * 1e-9 * m["dichte_platte"] + v_massiv * 1e-9 * m["dichte_massiv"]
    kgm = lambda b, h, w: (2 * (b + h) * w - 4 * w * w) * 7.85e-3        # kg/m Rechteckrohr
    st_h = d["rand_top"] - k["fuss_h"] - ra["rohr_h"]
    rahmen = (2 * (L - 2 * t) * kgm(ra["rohr_b"], ra["rohr_h"], ra["rohr_t"])
              + 2 * len(d["stuetze_x"]) * st_h * kgm(ra["stuetze"], ra["stuetze"], 2)
              + 2 * len(d["stuetze_x"]) * (d["stuetze_y"][1] - d["stuetze_y"][0]) * kgm(ra["stuetze"], ra["stuetze"], 2)
              + 4 * d["fach_breiten"][0] * ra["traverse_b"] * ra["traverse_t"] * 7.85e-3) * 1e-3
    mechanik = (2 * (lb["l"] + st["l"]) * me["bein_breite"] * me["bein_dicke"] * 7.85e-6
                + 2 * d["stab_l"] * me["bein_breite"] * me["bein_dicke"] * 7.85e-6
                + 2 * ((lb["schiene_x1"] - lb["schiene_x0"]) + (st["schiene_x1"] - st["schiene_x0"])) * 1.5e-3
                + 6 * 110 * 70 * me["gelenkplatte"] * 7.85e-6 + 0.1 * len([i for i in platz if i["typ"] == "khr"]))
    fahrwerk = 6.0
    schaum = (lb["laenge"] + st["laenge"]) * d["pad_b"] * po["schaum"] * 1e-9 * 45
    rest = 3.0
    leer = holz + rahmen + mechanik + fahrwerk + schaum + rest
    flaeche_platte = (mantel + platten + innen + (lb["laenge"] + st["laenge"]) * d["pad_b"]) * 1e-6
    flaeche_massiv = (d["rt_len"] * d["innen_h"] + rr_umfang(L - 2 * se, D - 2 * se, R - se) * (sh - fh)) * 1e-6
    return {"holz": holz, "rahmen": rahmen, "mechanik": mechanik, "fahrwerk": fahrwerk, "schaum": schaum,
            "rest": rest, "leer": leer, "flaeche_platte": flaeche_platte, "flaeche_massiv": flaeche_massiv}


def fmt(x, n=1):
    return f"{x:,.{n}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def zahl(x):
    return fmt(x, 0 if float(x).is_integer() else 1)


def write_stueckliste(p, d, liste, platz, gw):
    m = p["material"]
    inhalt = sum(i["kg"] for i in platz)
    k_platte = gw["flaeche_platte"] * 1.25 * m["preis_platte_m2"]
    k_massiv = gw["flaeche_massiv"] * 1.3 * m["preis_massiv_m2"]
    holz_mat = k_platte + k_massiv
    out = ["# Stückliste (Planungsstand)", "",
           "> Automatisch erzeugt aus `params.toml` mit `python3 tools/build.py`. Nicht von Hand ändern.",
           "> Planungsstand für Angebot und Abstimmung, **keine Zuschnittliste**: Die erstellt der Schreiner nach "
           "Abschluss der Beschlagplanung (siehe Studio-Vorentwurf).", ""]
    for gruppe in dict.fromkeys(g for g, *_ in liste):
        out += [f"## {gruppe}", "",
                "| Teil | Stk. | Länge | Breite | Dicke | Hinweis |",
                "|---|---:|---:|---:|---:|---|"]
        for g, name, n, l, b, dicke, hinweis in liste:
            if g == gruppe and n:
                out.append(f"| {name} | {n} | {zahl(l) if l else '–'} | {zahl(b) if b else '–'} | {zahl(dicke) if dicke else '–'} | {hinweis} |")
        out.append("")
    po = p["polster"]
    zug = 2 * (po["schaum"] + 60)
    lb, st = d["teile"]["lehne"], d["teile"]["sitz"]
    leder = ((st["laenge"] + zug) * (d["pad_b"] + zug) + (lb["laenge"] + zug) * (d["pad_b"] + zug)) * 1e-6
    out += ["Maße in mm.", "",
            "## Polster", "",
            f"- Schaumstoff je Polster {po['schaum']} mm: fest (RG 50+) unten, mittel (RG 35–40) oben, Watte darüber",
            f"- Bezug ca. {fmt(leder, 2)} m² Rindleder Cognac, vollnarbig, pigmentiert oder Semianilin, Kedernaht",
            "- Bezug und Polster austauschbar: Polsterplatte von unten verschraubt, Leder auf eigenem Spannrahmen oder getackert", "",
            "## Gewicht", "",
            f"- Holz {fmt(gw['holz'])} kg, Innenrahmen {fmt(gw['rahmen'])} kg, Mechanik und Hantelaufnahmen {fmt(gw['mechanik'])} kg, "
            f"Fahrwerk {fmt(gw['fahrwerk'])} kg, Polster und Kleinteile {fmt(gw['schaum'] + gw['rest'])} kg",
            f"- Bank leer: ca. **{fmt(gw['leer'])} kg**, mit Hanteln und Zubehör ({fmt(inhalt)} kg): ca. **{fmt(gw['leer'] + inhalt)} kg**", "",
            "## Kosten (Schätzung, getrennt nach Gewerken wie im Vorentwurf)", "",
            "| Gewerk | Inhalt | Kosten |", "|---|---|---:|",
            f"| Holzbau | Platten {fmt(gw['flaeche_platte'], 1)} m² furniert + Eiche massiv {fmt(gw['flaeche_massiv'], 1)} m² (ca. {fmt(holz_mat, 0)} €), "
            "Rundungen, Rolltür, Oberfläche, Montage, grob 50–80 h | 4.000–7.000 € |",
            "| Polster | Leder, Schaum, Polsterarbeit für 2 Polster | 600–1.000 € |",
            "| Metallbau und Beschläge | Innenrahmen geschweißt und beschichtet, 2 Gleitstützen mit Indexbolzen, Gelenke, 10 Hantelaufnahmen | 1.500–3.000 € |",
            "| Fahrwerk | Rollenrahmen, 4 Lenkrollen, Exzenterwellen, Bronze-Pedal | 500–1.200 € |",
            "| **Gesamt grob** | | **6.600–12.200 €** |",
            "| Option | Elektrischer Taster mit Spindelantrieb statt Pedal | + 400–900 € |", "",
            "Ohne Hanteln (siehe hanteln.md). Grobe Annahmen, regional sehr verschieden. "
            "Das Angebot bitte getrennt nach diesen vier Gewerken anfragen.", ""]
    (ROOT / "docs" / "stueckliste.md").write_text("\n".join(out))
    return inhalt


def write_berechnung(p, d, platz, fehlt, belegt, gw, inhalt, rast, pruef):
    me, last, k, po, ro, ra = p["mechanik"], p["last"], p["korpus"], p["polster"], p["rollen"], p["rahmen"]

    def ok(w, g):
        return "✅" if w <= g else "⚠️"

    out = ["# Berechnung", "",
           "> Automatisch erzeugt aus `params.toml` mit `python3 tools/build.py`. Nicht von Hand ändern.",
           "> Überschlagsrechnung zur Abstimmung. Den Nachweis von Lasten, Verbindungen, Verriegelung und "
           "Kippsicherheit übernehmen Metallbau bzw. Beschlaglieferant.", "",
           "## Hauptmaße", "",
           f"- Außen: {d['L']} × {d['D']} × {d['H']} mm (L × T × H), Ecken im Grundriss R {d['R']}",
           f"- Längskette: {po['luft_ende'] + d['t']} + Lehne {fmt(d['lehne_l'], 0)} + Fuge {po['fuge']} + Sitz {po['sitz_laenge']} + {po['luft_ende'] + d['t']} = {d['L']} mm",
           f"- Polsterbreite {d['pad_b']} mm (Rand {d['t']} + Spalt {po['luft_seite']} je Seite für die Gelenkkonsolen)",
           f"- Höhe: Sockel {k['sockel_hoehe']} + Korpus {d['korpus_h']} + Polsterpaket {d['polster_h']} = {d['H']} mm",
           f"- Rolltür {fmt(d['rt_len'], 0)} mm aus {d['rt_n']} Lamellen à {fmt(d['rt_b'])} mm, Speicherweg links und hinten "
           f"{fmt(d['rt_speicher'], 0)} mm " + ("✅" if d["rt_speicher"] >= d["rt_len"] else "⚠️ zu kurz"),
           f"- Innenraum: Tasche {k['tasche']} mm, Hantelbereich {fmt(d['fach_breiten'][0], 0)} mm, Zubehör {fmt(d['fach_breiten'][1], 0)} mm, "
           f"{fmt(d['fach_tiefe'], 0)} mm tief, {d['innen_h']} mm hoch", ""]

    for teil in TEILE:
        tl = d["teile"][teil]
        rs, F_last = rast[teil]
        rfehler, rabst = pruef[teil]
        q = p[teil]
        seite = "linke" if tl["dir"] < 0 else "rechte"
        out += [f"## {NAME[teil]}", "",
                f"Gemeinsame Drehachse mit dem anderen Polster in der Mitte der Fuge, {me['achse_unter_oberkante']} mm unter der Polsteroberfläche "
                f"(x = {fmt(tl['achse_x'], 0)} mm ab linkem Ende). Das {seite} Ende hebt sich. "
                f"Die Gleitstütze ist {tl['s']} mm von der Achse angelenkt und {tl['l']} mm lang. "
                f"Ihr Fuß gleitet in einer C-Schiene und wird in jeder Arbeitsstellung von einem federnden Indexbolzen Ø {me['bolzen_d']} "
                "formschlüssig verriegelt. Flach liegt das Polster auf dem Rahmen, der Gleitschuh steht am Endanschlag "
                "und wird von einem Kugelschnäpper gegen Abheben gehalten.", "",
                f"Last: {int(q['last_anteil'] * 100)} % von {last['nutzer_kg']} kg × {last['dynamik']} = {fmt(F_last, 0)} N, "
                f"{q['last_abstand']} mm von der Achse, senkrecht nach unten oder senkrecht auf das Polster. "
                "Die Tabelle zeigt den ungünstigeren Fall.", "",
                "| Stellung | Loch / Anschlag ab Achse | ab linkem Ende | Stützkraft | Achskraft | Neigung Stütze |",
                "|---|---:|---:|---:|---:|---:|"]
        for r in rs:
            if r["ok"]:
                out.append(f"| {r['winkel']}° | {fmt(r['n'], 0)} mm | {fmt(gx(tl, r['n']), 0)} mm | "
                           + (f"{fmt(r['F'], 0)} N | {fmt(r['R'], 0)} N |" if r["winkel"] else "– | – |")
                           + f" {fmt(r['neigung'], 0)}° |")
            else:
                out.append(f"| {r['winkel']}° | – | – | – | – | nicht erreichbar |")
        F_max = max((r["F"] for r in rs if r["ok"]), default=0)
        F_cr, sk = knicken(p, d, teil, F_max)
        tau = F_max / 2 / (2 * math.pi * me["bolzen_d"] ** 2 / 4)
        out += ["",
                f"- Kleinster Lochabstand {fmt(rabst, 0)} mm (Minimum {me['loch_abstand_min']} mm). "
                "Ein eigenes Loch für flach ginge nicht: Es läge nur gut 10 mm neben dem Loch für den kleinsten Winkel.",
                f"- Knicken der Stütze (2 × Flachstahl {me['bein_breite']} × {me['bein_dicke']}): "
                f"Knicklast {fmt(F_cr / 1000, 1)} kN bei max. {fmt(F_max / 1000, 2)} kN → Sicherheit ≈ {fmt(sk, 1)}.",
                f"- Indexbolzen Ø {me['bolzen_d']}, je Bein zweischnittig: Scherspannung ≈ {fmt(tau, 0)} N/mm² (Stahl zulässig > 100 N/mm²).",
                "", ("**⚠️ Geometrie prüfen:** " + "; ".join(rfehler)) if rfehler
                else "✅ Alle Löcher liegen auf der Schiene und haben genug Abstand.", ""]

    spiel, al, as_ = fuge_pruefen(p, d)
    out += ["## Fuge zwischen Lehne und Sitz", "",
            f"Lehne und Sitz drehen um eine gemeinsame Achse in der Fugenmitte, {me['achse_unter_oberkante']} mm unter der Oberfläche. "
            f"Die Polsterkanten sind mit R {po['radius']} gerundet und wandern beim Anstellen nur wenig in die Fuge. Kleinster Abstand über alle Stellungen: "
            f"**{fmt(spiel, 1)} mm** (Lehne {al}°, Sitz {as_}°, Fuge {po['fuge']} mm). "
            + ("✅" if spiel >= me["min_spiel"] else f"⚠️ weniger als {me['min_spiel']} mm"), "",
            "Mit einer Achse unten am Polster, wie in der Funktionsskizze des Vorentwurfs angedeutet, würden die oberen Kanten "
            f"bei 60° rund {fmt(d['polster_h'] * math.sin(math.radians(60)), 0)} mm in die Fuge wandern. "
            "Deshalb sitzt die Achse oben, getragen von schmalen Konsolen im Spalt neben den Polstern. "
            "Zwei getrennte Achsen gingen bei so kleiner Fuge nicht: Zwei Bolzen M10 brauchen mehr als 16 mm Abstand.", ""]

    out += ["## Stauraum", "",
            "Hanteln einzeln in Aufnahmen auf Stahltraversen zwischen den Rahmenstützen, schwerste unten. Zubehör im Zubehörbereich; was in der Tiefe an die Stützen reicht, liegt daneben (die Matte quer).", "",
            "| Bereich | Inhalt | Breite | Höhe | Tiefe | kg |", "|---|---|---:|---:|---:|---:|"]
    for i in sorted(platz, key=lambda i: (i["fach"], i["ebene"] == "oben", i["x"])):
        out.append(f"| {i['zelle']} | {i['name']} | {fmt(i['w'], 0)} | {fmt(i['h'], 0)} | {fmt(i['d'], 0)} | {fmt(i['kg'])} |")
    out += ["", "| Bereich | lichte Höhe | belegt / verfügbar (Breite) | davon vorn offen |", "|---|---:|---:|---:|"]
    for z in sorted(d["zellen"], key=lambda z: (z["fach"], z["ebene"] == "oben")):
        out.append(f"| {z['name']} | {fmt(z['zugang'], 0)} mm | {fmt(belegt[z['name']], 0)} / {fmt(z['breite'], 0)} mm | {fmt(z['offen'], 0)} mm |")
    out += ["", ("**⚠️ Passt nicht:** " + ", ".join(i["name"] for i in fehlt)) if fehlt
            else "✅ Alle 10 Hanteln und das Zubehör finden Platz.",
            "", "Die Breiten gelten für die selbstgebauten Hanteln aus [hanteln.md](hanteln.md). "
            "Vor der Fertigung werden die fertigen Hanteln vermessen und die Aufnahmen danach gesetzt.", ""]

    out += ["## Durchbiegung", "",
            f"Lastannahme: {last['nutzer_kg']} kg Nutzer × Stoßfaktor {last['dynamik']}. Die Lasten laufen über den Innenrahmen "
            "direkt in die Füße, die Holzverkleidung trägt nicht mit.", "",
            "| Bauteil | Last | Stützweite | Durchbiegung | Grenze L/300 | |",
            "|---|---:|---:|---:|---:|---|"]
    for name, F, l, w in statik(p, d, platz, rast):
        out.append(f"| {name} | {fmt(F, 0)} N | {fmt(l, 0)} mm | {fmt(w, 2)} mm | {fmt(l / 300, 2)} mm | {ok(w, l / 300)} |")
    out.append("")

    fx = [f_[0] for f_ in d["fuss_pos"]]
    fy = [f_[1] for f_ in d["fuss_pos"]]
    r_f = k["fuss_d"] / 2
    x_l, x_r = min(fx) - r_f, max(fx) + r_f
    y_v, y_h = min(fy) - r_f, max(fy) + r_f
    out += ["## Kippsicherheit", "",
            f"Die Füße sitzen unter den Eckstützen des Innenrahmens. Standfläche x = {fmt(x_l, 0)}…{fmt(x_r, 0)} mm, "
            f"y = {fmt(y_v, 0)}…{fmt(y_h, 0)} mm.", "",
            "| Fall | leer | mit Hanteln |", "|---|---:|---:|"]
    W = [gw["leer"], gw["leer"] + inhalt]
    for label, hebel, ueber in (("an der Längskante", d["D"] / 2 - y_v, d["pad_y0"] - y_v),
                                ("am linken Lehnenende", d["L"] / 2 - x_l, x_l - d["lehne_x0"]),
                                ("am rechten Sitzende", x_r - d["L"] / 2, d["sitz_x1"] - x_r)):
        if ueber <= 0:
            out.append(f"| Senkrechte Last {label} | liegt innerhalb der Standfläche | kippt nicht |")
        else:
            w_ = [w * hebel / ueber for w in W]
            out.append(f"| Senkrechte Last {label}, ab der die Bank kippt | {fmt(w_[0], 0)} kg | {fmt(w_[1], 0)} kg |")
    lb = d["teile"]["lehne"]
    h_top = d["achse_z"] + lb["laenge"] * math.sin(math.radians(max(lb["winkel"])))
    kipp = [w * G * (d["L"] / 2 - x_l) / h_top for w in W]
    out.append(f"| Lehne {max(lb['winkel'])}°: waagerechter Druck nach hinten an der Lehnenoberkante ({fmt(h_top, 0)} mm hoch), niemand sitzt | "
               f"{fmt(kipp[0], 0)} N | {fmt(kipp[1], 0)} N |")
    out += ["", f"Zum Vergleich: {last['nutzer_kg']} kg × {last['dynamik']} = {fmt(last['nutzer_kg'] * last['dynamik'], 0)} kg. "
            "Step-ups oder Aufstützen genau am Lehnenende sind damit abgedeckt; die Lehne ist aber kein Griff zum Hochziehen.", ""]

    kraft = [w * G * ro["hub"] / ro["pedalweg"] * 1.3 for w in W]
    out += ["## Fahrwerk", "",
            f"- Trainieren: Die Bank steht auf 4 Stellfüßen an den Eckstützen. Die {ro['anzahl']} Lenkrollen Ø {ro['durchmesser']} haben Bodenfreiheit.",
            f"- Rollen: Bronze-Pedal rechts im Sockel treten. Zwei gekoppelte Exzenterwellen senken den geführten Rollenrahmen ab und heben die Füße {ro['hub']} mm an.",
            f"- Pedalkraft (≈ {ro['pedalweg']} mm Weg, mit Reibung): leer ≈ {fmt(kraft[0] / G, 0)} kg, mit Hanteln ≈ {fmt(kraft[1] / G, 0)} kg.",
            "- Transportstellung über Totpunkt verriegelt. Beim Verschieben: Polster flach, Rolltür zu, niemand auf der Bank.",
            "- Option: elektrischer Taster mit Spindelantrieb statt Pedal.", ""]
    (ROOT / "docs" / "berechnung.md").write_text("\n".join(out))


def write_hanteln(p, hs, m_griff):
    h = p["hanteln"]
    rho = h["dichte_stahl"] * 1e-9
    roh_kg = sum(2 * math.pi / 4 * (x["D"] + 3) ** 2 * (x["lk"] + h["zugabe"] + 3) * rho for x in hs)
    ab = h["abflachung"]
    out = ["# Hanteln", "",
           "> Automatisch erzeugt aus `params.toml` mit `python3 tools/build.py`. Nicht von Hand ändern.", "",
           "Fünf Paar Kurzhanteln, passend zur Bank: schwarze Stahlköpfe, Griff aus Eiche. "
           "In der Bank hängt jede Hantel einzeln in einer gepolsterten Aufnahme am Griff, gesichert mit einem Bügel "
           "(Belegung siehe [berechnung.md](berechnung.md)). Die freie Grifflänge zwischen den Auflagen bleibt frei.", "",
           "![Hantel](zeichnungen/hantel.svg)", "",
           "## Aufbau", "",
           f"- **Köpfe:** Rundstahl S235, gedreht. Fase {h['fase']} × 45° an allen Kanten, zentrisches Sackloch M16 × {h['gewinde_tiefe']} mm"
           + (f", {ab} mm tiefe Abflachung. Mit ihr rollt die Hantel auf dem Boden nicht weg." if ab else "."),
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
    ("moebel.png", "600,215,230,72,0,22,2500", "p", {}),
    ("training.png", "600,215,420,68,0,22,3300", "p",
     {"lehne_winkel": "45", "sitz_winkel": "15", "rolltuer_offen": "true"}),
    ("verstellung.png", "600,0,650,90,0,0,2800", "o",
     {"lehne_winkel": "45", "sitz_winkel": "15", "geist": "true", "zeige_inhalt": "false"}),
    ("stauraum.png", "600,215,230,72,0,22,2500", "p", {"rolltuer_offen": "true"}),
    ("tragwerk.png", "600,215,250,68,0,22,2700", "p",
     {"zeige_holz": "false", "lehne_winkel": "30", "sitz_winkel": "10"}),
    ("explosion.png", "600,215,320,66,0,22,3300", "p", {"explosion": "1"}),
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
    rast = {teil: rasten(p, d, teil) for teil in TEILE}
    pruef = {teil: pruefe_rasten(p, d, teil, rast[teil][0]) for teil in TEILE}
    hs, m_griff = hanteln(p)
    platz, fehlt, belegt = pack(p, d, hs)
    write_scad(p, d, platz, rast)
    gw = gewicht(p, d, platz)
    inhalt = write_stueckliste(p, d, teile(p, d, platz), platz, gw)
    write_berechnung(p, d, platz, fehlt, belegt, gw, inhalt, rast, pruef)
    write_hanteln(p, hs, m_griff)
    zeichnungen.erzeuge(ROOT / "docs" / "zeichnungen", p, d, rast, hs)
    print("cad/params.scad, docs/stueckliste.md, docs/berechnung.md, docs/hanteln.md, docs/zeichnungen/ geschrieben")
    for teil in TEILE:
        for w in pruef[teil][0]:
            print(f"WARNUNG {NAME[teil]}:", w)
    spiel = fuge_pruefen(p, d)[0]
    if spiel < p["mechanik"]["min_spiel"]:
        print(f"WARNUNG Fuge: nur {spiel:.1f} mm Abstand zwischen den Polsterkanten")
    if fehlt:
        print("WARNUNG – passt nicht in den Stauraum:", ", ".join(i["name"] for i in fehlt))
    if "--no-render" not in sys.argv:
        render()


if __name__ == "__main__":
    main()
