#!/usr/bin/env python3
"""Erzeugt aus params.toml alle abgeleiteten Dateien der Bank.

- cad/params.scad       Parameter + abgeleitete Maße für das OpenSCAD-Modell
- docs/stueckliste.md   Zuschnittliste, Beschläge, Gewicht, grobe Kosten
- docs/berechnung.md    Stauraum-Belegung, Durchbiegung, Kippsicherheit
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


def load_params():
    with open(ROOT / "params.toml", "rb") as f:
        return tomllib.load(f)


def derive(p):
    """Alle abgeleiteten Maße an einer Stelle – SCAD und Doku nutzen dieselben Werte."""
    b, m, po, k, tu = p["bank"], p["material"], p["polster"], p["korpus"], p["tueren"]
    L, D, H = b["laenge"], b["tiefe"], b["hoehe"]
    t = m["platte"]
    d = {"L": L, "D": D, "H": H, "t": t, "tt": m["tuer"]}

    d["polster_h"] = po["platte"] + po["schaum"]
    d["deckel_z1"] = H - d["polster_h"]
    d["deckel_z0"] = d["deckel_z1"] - t
    d["seite_h"] = d["deckel_z0"]
    d["boden_z0"] = k["fuss_hoehe"]
    d["boden_z1"] = k["fuss_hoehe"] + t
    d["innen_l"] = L - 2 * t
    d["innen_h"] = d["deckel_z0"] - d["boden_z1"]
    d["leiste_z0"] = d["deckel_z0"] - tu["leiste_hoehe"]
    d["rueck_y0"] = D - t
    d["fach_y0"] = tu["leiste_tiefe"]
    d["fach_tiefe"] = d["rueck_y0"] - d["fach_y0"]

    n_mw = k["mittelwaende"]
    d["n_mw"] = n_mw
    d["n_fach"] = n_mw + 1
    d["fach_breite"] = (d["innen_l"] - n_mw * t) / d["n_fach"]
    d["fach_x0"] = [t + i * (d["fach_breite"] + t) for i in range(d["n_fach"])]

    if k["fachboden"]:
        d["zelle_h"] = (d["innen_h"] - t) / 2
        d["fachboden_z0"] = d["boden_z1"] + d["zelle_h"]
        d["fachboden_z1"] = d["fachboden_z0"] + t
    else:
        d["zelle_h"] = d["innen_h"]
        d["fachboden_z0"] = d["fachboden_z1"] = None

    # Laufspuren: von hinten aus der Führungsleiste heraus gerechnet, Stege je 3 mm
    nb, steg = tu["nut_breite"], 3
    spur2_y0 = tu["leiste_tiefe"] - steg - nb
    spur1_y0 = spur2_y0 - steg - nb
    d["spur_y0"] = [spur1_y0, spur2_y0]
    d["nut_breite"] = nb
    luft = (nb - m["tuer"]) / 2
    d["tuer_y0"] = [spur1_y0 + luft, spur2_y0 + luft]

    oeffnung = d["leiste_z0"] - d["boden_z1"]
    eintauchen_oben = tu["nut_oben"] - tu["nut_unten"] - 2   # Einhängen: hochschieben, unten einsetzen
    d["tuer_oeffnung"] = oeffnung
    d["tuer_h"] = oeffnung + tu["nut_unten"] + eintauchen_oben
    d["tuer_z0"] = d["boden_z1"] - tu["nut_unten"]
    n_t = tu["anzahl"]
    d["n_tuer"] = n_t
    d["tuer_l"] = (d["innen_l"] + (n_t - 1) * tu["ueberlappung"]) / n_t
    d["tuer_x0"] = [t + i * (d["tuer_l"] - tu["ueberlappung"]) for i in range(n_t)]

    # Zugangshöhe je Zelle: oben begrenzt durch Fachboden bzw. Führungsleiste
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
                "h": z1 - z0, "zugang": min(z1, d["leiste_z0"]) - z0,
                "breite": d["fach_breite"], "tiefe": d["fach_tiefe"],
            })
    # Schweres nach unten: erst alle unteren Zellen, dann die oberen
    zellen.sort(key=lambda z: (z["ebene"] == "oben", z["fach"]))
    d["zellen"] = zellen
    return d


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


def write_scad(p, d, platz):
    k, tu, r, g, po = p["korpus"], p["tueren"], p["rollen"], p["griff"], p["polster"]
    werte = {
        "L": d["L"], "D": d["D"], "H": d["H"], "t": d["t"], "tt": d["tt"],
        "polster_platte": po["platte"], "polster_schaum": po["schaum"], "polster_r": po["radius"],
        "deckel_z0": d["deckel_z0"], "deckel_z1": d["deckel_z1"], "seite_h": d["seite_h"],
        "boden_z0": d["boden_z0"], "boden_z1": d["boden_z1"],
        "innen_l": d["innen_l"], "innen_h": d["innen_h"],
        "fuss_h": k["fuss_hoehe"], "fuss_b": k["fuss_breite"], "sockel_versatz": k["sockel_versatz"],
        "leiste_h": tu["leiste_hoehe"], "leiste_t": tu["leiste_tiefe"], "leiste_z0": d["leiste_z0"],
        "nut_breite": d["nut_breite"], "nut_oben": tu["nut_oben"], "nut_unten": tu["nut_unten"],
        "spur_y0": d["spur_y0"],
        "rueck_y0": d["rueck_y0"], "fach_y0": d["fach_y0"], "fach_tiefe": d["fach_tiefe"],
        "fach_breite": d["fach_breite"], "fach_x0": d["fach_x0"], "n_mw": d["n_mw"],
        "fachboden": k["fachboden"],
        "fachboden_z0": d["fachboden_z0"] or 0, "fachboden_z1": d["fachboden_z1"] or 0,
        "tuer_x0": d["tuer_x0"], "tuer_y0": d["tuer_y0"], "tuer_l": d["tuer_l"],
        "tuer_h": d["tuer_h"], "tuer_z0": d["tuer_z0"],
        "schlitz_b": tu["schlitz_breite"], "schlitz_abst": tu["schlitz_abstand"],
        "schlitz_rand": tu["schlitz_rand"],
        "rollen": r["aktiv"], "rolle_d": r["durchmesser"], "rolle_b": r["breite"],
        "rolle_luft": r["bodenfreiheit"],
        "griff_b": g["breite"], "griff_h": g["hoehe"], "griff_oben": g["abstand_oben"],
        # [typ, x, y, z, breite, hoehe, tiefe, kopf]
        "inhalt": [[i["typ"], i["x"], i["y"], i["z"], i["w"], i["h"], i["d"], i.get("kopf", 0)]
                   for i in platz],
        "abstand": p["inventar"]["abstand"],
    }
    lines = ["// AUTOMATISCH ERZEUGT von tools/build.py aus params.toml – nicht von Hand ändern.", ""]
    lines += [f"{k_} = {scad_value(v)};" for k_, v in werte.items()]
    (ROOT / "cad" / "params.scad").write_text("\n".join(lines) + "\n")


def teile(p, d):
    """Zuschnittliste: (Bezeichnung, Anzahl, Länge, Breite, Dicke, Material, Hinweis, Abzug_mm2)."""
    t, tt, k, tu, g = d["t"], d["tt"], p["korpus"], p["tueren"], p["griff"]
    fuss_ausschnitt = (d["D"] - 2 * k["fuss_breite"]) * k["fuss_hoehe"]
    griff = g["breite"] * g["hoehe"]
    n_schlitze = schlitze_pro_tuer(p, d)
    schlitz_flaeche = n_schlitze * tu["schlitz_breite"] * (d["tuer_h"] - 2 * tu["schlitz_rand"])
    liste = [
        ("Seitenwange", 2, d["D"], d["seite_h"], t, "Birke Multiplex",
         f"Fußausschnitt {d['D'] - 2 * k['fuss_breite']}×{k['fuss_hoehe']}; links Griffloch {g['breite']}×{g['hoehe']}",
         fuss_ausschnitt + griff / 2),
        ("Deckel", 1, d["L"], d["D"], t, "Birke Multiplex", "liegt auf den Wangen auf", 0),
        ("Boden", 1, d["innen_l"], d["D"], t, "Birke Multiplex",
         f"2 Laufnuten {d['nut_breite']}×{tu['nut_unten']}", 0),
        ("Rückwand", 1, d["innen_l"], d["innen_h"], t, "Birke Multiplex", "tragend, verleimt", 0),
        ("Sockelblende", 2, d["innen_l"], k["fuss_hoehe"], t, "Birke Multiplex",
         f"vorne {k['sockel_versatz']} mm zurückgesetzt, hinten bündig", 0),
    ]
    if d["n_mw"]:
        liste.append(("Mittelwand", d["n_mw"], d["fach_tiefe"], d["innen_h"], t, "Birke Multiplex",
                      "Bohrreihe für Bodenträger", 0))
    if k["fachboden"]:
        liste.append(("Fachboden", d["n_fach"], round(d["fach_breite"] - 2, 1), d["fach_tiefe"] - 5, t,
                      "Birke Multiplex", "auf Bodenträgern, Filz/Kork belegt", 0))
    liste += [
        ("Schiebetür", d["n_tuer"], round(d["tuer_l"], 1), d["tuer_h"], tt, "Birke Multiplex",
         f"{n_schlitze} Lüftungsschlitze {tu['schlitz_breite']} mm", schlitz_flaeche),
        ("Polster-Trägerplatte", 1, d["L"], d["D"], p["polster"]["platte"], "Birke Multiplex",
         "4 Bohrungen für Zentrierbolzen", 0),
        ("Führungsleiste", 1, d["innen_l"], tu["leiste_tiefe"], tu["leiste_hoehe"], "Buche massiv",
         f"2 Nuten {d['nut_breite']}×{tu['nut_oben']} unten", 2 * d["nut_breite"] * tu["nut_oben"]),
    ]
    return liste


def schlitze_pro_tuer(p, d):
    tu = p["tueren"]
    nutzbar = d["tuer_l"] - 2 * tu["schlitz_rand"]
    return int(nutzbar // tu["schlitz_abstand"]) + 1


def gewicht_holz(p, d, liste):
    m = p["material"]
    kg = 0.0
    for name, n, l, b, dicke, mat, _, abzug in liste:
        rho = m["dichte_leiste"] if "massiv" in mat else m["dichte_platte"]
        if name == "Führungsleiste":
            vol = (l * b * dicke - l * abzug) * 1e-9 * n
        else:
            vol = (l * b - abzug) * dicke * 1e-9 * n
        kg += vol * rho
    return kg


def flaechen(liste):
    f = {}
    for _, n, l, b, dicke, mat, _, _ in liste:
        if "Multiplex" in mat:
            f[dicke] = f.get(dicke, 0) + n * l * b * 1e-6
    return f


def biegung_front(p, d):
    """Vordere Kante = Deckelstreifen + Führungsleiste als verleimter Verbundträger."""
    m, tu, t = p["material"], p["tueren"], d["t"]
    b_eff = 100   # mitwirkende Deckelbreite, konservativ
    lh, lt, nb, no = tu["leiste_hoehe"], tu["leiste_tiefe"], d["nut_breite"], tu["nut_oben"]
    # Rechtecke: (Breite, Höhe, z-Unterkante, E, Vorzeichen)
    rect = [(lt, lh, 0, m["E_leiste"], 1),
            (nb, no, 0, m["E_leiste"], -1),
            (nb, no, 0, m["E_leiste"], -1),
            (b_eff, t, lh, m["E_flach"], 1)]
    EA = sum(s * E * bb * hh for bb, hh, _, E, s in rect)
    z_s = sum(s * E * bb * hh * (z0 + hh / 2) for bb, hh, z0, E, s in rect) / EA
    EI = sum(s * E * (bb * hh ** 3 / 12 + bb * hh * (z0 + hh / 2 - z_s) ** 2)
             for bb, hh, z0, E, s in rect)
    last = p["last"]
    F = last["nutzer_kg"] * G * last["dynamik"] * last["anteil_front"]
    l = d["fach_breite"] + t   # Stützweite Mitte–Mitte der Wände
    w = F * l ** 3 / (48 * EI)
    M = F * l / 4
    sigma = M * z_s / EI * m["E_leiste"]   # Unterkante Leiste
    return {"F": F, "l": l, "EI": EI, "w": w, "sigma": sigma, "grenze": l / 300}


def biegung_deckel(p, d):
    """Deckel als Platte zwischen Rückwand und Führungsleiste, Polsterplatte nicht angesetzt."""
    m, last = p["material"], p["last"]
    F = last["nutzer_kg"] * G * last["dynamik"]
    l = d["fach_tiefe"]
    b = min(300, d["fach_breite"])
    I = b * d["t"] ** 3 / 12
    w = 5 * F * l ** 3 / (384 * m["E_flach"] * I)
    return {"F": F, "l": l, "b": b, "w": w, "grenze": l / 300}


def biegung_fachboden(p, d, platz):
    m = p["material"]
    worst = None
    for f in range(d["n_fach"]):
        kg = sum(i["kg"] for i in platz if i["fach"] == f and i["ebene"] == "oben")
        F = kg * G * 2   # Faktor 2 für Abstellen/Stoßen
        l = d["fach_breite"]
        I = (d["fach_tiefe"] - 5) * d["t"] ** 3 / 12
        w = 5 * F * l ** 3 / (384 * m["E_flach"] * I)
        if worst is None or w > worst["w"]:
            worst = {"fach": f + 1, "kg": kg, "w": w, "l": l, "grenze": l / 300}
    return worst


def ankippen(p, d):
    """Winkel und Hubhöhe, bis die Rollen an der rechten Stirnseite greifen."""
    r = p["rollen"]
    rad = r["durchmesser"] / 2
    dx = rad + 2          # Rollenmitte vor der Stirnseite
    zc = rad + r["bodenfreiheit"]
    a = 0.0
    while zc * math.cos(a) - dx * math.sin(a) > rad and a < math.radians(45):
        a += math.radians(0.1)
    return math.degrees(a), d["L"] * math.sin(a)


def fmt(x, n=1):
    s = f"{x:,.{n}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return s


def write_stueckliste(p, d, liste, platz):
    m = p["material"]
    f = flaechen(liste)
    holz = gewicht_holz(p, d, liste)
    po = p["polster"]
    schaum_kg = d["L"] * d["D"] * po["schaum"] * 1e-9 * 45
    rest_kg = 1.0 + 1.5 + (0.6 if p["rollen"]["aktiv"] else 0)  # Bezug, Beschläge, Rollen
    leer = holz + schaum_kg + rest_kg
    inhalt = sum(i["kg"] for i in platz)
    preis = {18: m["preis_m2_18"], 15: m["preis_m2_18"], 12: m["preis_m2_12"]}
    kosten_platten = sum(a * 1.15 * preis.get(dicke, m["preis_m2_18"]) for dicke, a in f.items())
    zugabe = 2 * (d["polster_h"] + 80)
    bezug = ((d["L"] + zugabe) / 1000, (d["D"] + zugabe) / 1000)

    out = ["# Stückliste", "",
           "> Automatisch erzeugt aus `params.toml` mit `python3 tools/build.py`. Nicht von Hand ändern.", "",
           "## Zuschnitt", "",
           "| Teil | Stk. | Länge | Breite | Dicke | Material | Hinweis |",
           "|---|---:|---:|---:|---:|---|---|"]
    for name, n, l, b, dicke, mat, hinweis, _ in liste:
        out.append(f"| {name} | {n} | {fmt(l, 0 if float(l).is_integer() else 1)} | {fmt(b, 0 if float(b).is_integer() else 1)} | {dicke} | {mat} | {hinweis} |")
    out += ["", "Maße in mm. Länge = Faserrichtung der Deckfurniere (bei Multiplex optisch, nicht statisch relevant).", "",
            "## Plattenbedarf", "",
            "| Dicke | Fläche netto | mit 15 % Verschnitt |", "|---:|---:|---:|"]
    for dicke, a in sorted(f.items(), reverse=True):
        out.append(f"| {dicke} mm | {fmt(a, 2)} m² | {fmt(a * 1.15, 2)} m² |")
    out += ["", "## Polster", "",
            f"- Schaumstoff {d['L']} × {d['D']} × {po['schaum']} mm, Empfehlung: 30 mm hart (RG 50+) unten + 20 mm mittel (RG 35–40) oben",
            "- Vlies/Wattierung 100 g/m² über den Schaum (weichere Kanten, Bezug liegt glatter)",
            f"- Bezug ca. {fmt(bezug[0], 2)} × {fmt(bezug[1], 2)} m (inkl. Umschlag zum Tackern)",
            "- Untere Abdeckung (Staubschutz-Vlies) für die Polsterunterseite", "",
            "## Beschläge und Kleinteile", "",
            "| Teil | Menge | Zweck |", "|---|---:|---|",
            "| Holzdübel 8 mm oder Domino/Lamello | ca. 40 | Korpusverbindungen, verleimt |",
            "| Holzleim D3 | 1 Flasche | feuchtigkeitsbeständig (Schweiß, Wischen) |",
            f"| Bodenträger 5 mm mit Kippschutz | {4 * d['n_fach'] if p['korpus']['fachboden'] else 0} | Fachböden |",
            "| Zentrierbolzen/Möbelverbinder | 4 | Polster rutschfest und abnehmbar |",
            "| Einschlagmuttern M6 + Sterngriffschrauben | 4 | optional: Polster fest verschrauben |",
            f"| Rollen Ø {p['rollen']['durchmesser']} mm mit Achse/Halter | {2 if p['rollen']['aktiv'] else 0} | Transport durch Ankippen |",
            "| Antirutsch-Gummipads | 4 | unter die Füße, Bank darf beim Training nicht wandern |",
            "| Gleitband/Wachs | – | Laufnuten der Schiebetüren |",
            "| Filz oder Kork 3 mm | ca. 0,5 m² | Auflage in den Hantelfächern |",
            f"| Hartholz-Abstandshalter | ca. {len([i for i in platz if i['typ'] == 'kh']) * 2} | zwischen den Hanteln, Fingerschutz |",
            "| Hartwachsöl oder 2K-Lack | 0,75 l | Oberfläche |", "",
            "## Gewicht und Kosten (Schätzung)", "",
            f"- Holz: ca. {fmt(holz)} kg",
            f"- Bank leer inkl. Polster und Beschlägen: ca. **{fmt(leer)} kg**",
            f"- Inventar im Stauraum: {fmt(inhalt)} kg → gesamt ca. **{fmt(leer + inhalt)} kg**",
            f"- Platten inkl. Verschnitt: ca. {fmt(kosten_platten, 0)} € (Annahme {m['preis_m2_18']} €/m² für 18 mm)",
            "- Polster (Schaum, Bezug, Vlies): ca. 80–200 € je nach Bezugsmaterial",
            "- Beschläge, Rollen, Leim, Öl: ca. 60–100 €",
            f"- **Material gesamt: ca. {fmt(kosten_platten + 140, 0)}–{fmt(kosten_platten + 300, 0)} €** (ohne Hanteln und Werkzeug)", ""]
    (ROOT / "docs" / "stueckliste.md").write_text("\n".join(out))
    return leer, inhalt


def write_berechnung(p, d, platz, fehlt, belegt, leer, inhalt):
    fr = biegung_front(p, d)
    de = biegung_deckel(p, d)
    fb = biegung_fachboden(p, d, platz) if p["korpus"]["fachboden"] else None
    last = p["last"]

    def ok(w, g):
        return "✅" if w <= g else "⚠️"

    out = ["# Berechnung", "",
           "> Automatisch erzeugt aus `params.toml` mit `python3 tools/build.py`. Nicht von Hand ändern.",
           "> Überschlagsrechnung zur Plausibilisierung, kein Statik-Nachweis.", "",
           "## Hauptmaße", "",
           f"- Außen: {d['L']} × {d['D']} × {d['H']} mm (L × T × H), Sitz- = Trainingshöhe {d['H']} mm",
           f"- Polster: {d['polster_h']} mm ({p['polster']['platte']} mm Platte + {p['polster']['schaum']} mm Schaum)",
           f"- Fächer: {d['n_fach']} × {fmt(d['fach_breite'])} mm breit, {d['fach_tiefe']} mm tief, "
           + (f"je 2 Ebenen à {fmt(d['zelle_h'])} mm" if p["korpus"]["fachboden"] else f"{d['innen_h']} mm hoch"),
           f"- Schiebetüren: {d['n_tuer']} × {fmt(d['tuer_l'])} × {d['tuer_h']} mm, Durchgriffshöhe {d['tuer_oeffnung']} mm", "",
           "## Stauraum-Belegung", "",
           "Schwerste Teile zuerst, untere Ebene zuerst. Zelle = Fach + Ebene.", "",
           "| Zelle | Inhalt | Breite | Höhe | Tiefe | kg |", "|---|---|---:|---:|---:|---:|"]
    for i in sorted(platz, key=lambda i: (i["fach"], i["ebene"] == "oben")):
        out.append(f"| {i['zelle']} | {i['name']} | {fmt(i['w'], 0)} | {fmt(i['h'], 0)} | {fmt(i['d'], 0)} | {fmt(i['kg'])} |")
    out += ["", "| Zelle | Zugangshöhe | belegt / verfügbar (Breite) |", "|---|---:|---:|"]
    for z in sorted(d["zellen"], key=lambda z: (z["fach"], z["ebene"] == "oben")):
        out.append(f"| {z['name']} | {fmt(z['zugang'], 0)} mm | {fmt(belegt[z['name']], 0)} / {fmt(z['breite'], 0)} mm |")
    if fehlt:
        out += ["", "**⚠️ Passt nicht:** " + ", ".join(i["name"] for i in fehlt)]
    else:
        out += ["", "✅ Alles Inventar findet Platz."]

    out += ["", "## Durchbiegung", "",
            f"Lastannahme: {last['nutzer_kg']} kg Nutzer × Stoßfaktor {last['dynamik']}.", "",
            "| Bauteil | Last | Stützweite | Durchbiegung | Grenze L/300 | |",
            "|---|---:|---:|---:|---:|---|",
            f"| Vorderkante (Deckel + Buchenleiste, Anteil {int(last['anteil_front'] * 100)} %) | {fmt(fr['F'], 0)} N | {fmt(fr['l'], 0)} mm | {fmt(fr['w'], 2)} mm | {fmt(fr['grenze'], 2)} mm | {ok(fr['w'], fr['grenze'])} |",
            f"| Deckel vorne→hinten (Streifen {de['b']} mm, volle Last) | {fmt(de['F'], 0)} N | {de['l']} mm | {fmt(de['w'], 2)} mm | {fmt(de['grenze'], 2)} mm | {ok(de['w'], de['grenze'])} |"]
    if fb:
        out.append(f"| Fachboden Fach {fb['fach']} ({fmt(fb['kg'])} kg × 2) | {fmt(fb['kg'] * G * 2, 0)} N | {fmt(fb['l'], 0)} mm | {fmt(fb['w'], 2)} mm | {fmt(fb['grenze'], 2)} mm | {ok(fb['w'], fb['grenze'])} |")
    out += ["",
            f"Biegespannung Unterkante Buchenleiste: {fmt(fr['sigma'])} N/mm² "
            f"(Buche massiv ~100 N/mm² Bruch → Sicherheit ≈ {fmt(100 / fr['sigma'], 0)}).",
            "Die Polster-Trägerplatte ist nicht angesetzt und bringt zusätzliche Reserve.", "",
            "## Kippsicherheit", "",
            "- Die Seitenwangen stehen bündig mit den Außenkanten auf dem Boden, das Polster steht nicht über.",
            "  **Senkrechte Lasten liegen immer innerhalb der Standfläche → die Bank kann durch Draufsitzen, Aufsteigen oder Abstützen an der Kante nicht kippen.**"]
    for label, kg in (("leer", leer), ("mit Inventar", leer + inhalt)):
        Fh = kg * G * (d["D"] / 2) / d["H"]
        out.append(f"- Waagerechte Kraft an der Polsteroberkante, die die Bank {label} seitlich kippt: ≈ {fmt(Fh, 0)} N (≈ {fmt(Fh / G, 0)} kg)")
    out.append("- Sitzt jemand auf der Bank, steigt dieser Wert um sein Körpergewicht × 0,44 – im Training unkritisch.")
    if p["rollen"]["aktiv"]:
        a, hub = ankippen(p, d)
        out += ["", "## Transport", "",
                f"- Rollen greifen ab ≈ {fmt(a)}° Neigung, d. h. linkes Ende am Griffloch um ≈ {fmt(hub, 0)} mm anheben.",
                f"- Am Griff anzuheben (halbes Gewicht, mit Inventar): ≈ {fmt((leer + inhalt) / 2, 0)} kg → schwere Hanteln vorher herausnehmen."]
    (ROOT / "docs" / "berechnung.md").write_text("\n".join(out) + "\n")


ANSICHTEN = [
    # Datei, Kamera (tx,ty,tz,rx,ry,rz,dist), Projektion, -D Optionen
    ("moebel.png", "600,200,200,70,0,25,2400", "p", {}),
    ("stauraum.png", "600,200,200,70,0,25,2400", "p", {"zeige_tueren": "false"}),
    ("explosion.png", "600,200,250,68,0,25,3200", "p", {"explosion": "1"}),
    ("front.png", "600,0,225,90,0,0,1900", "o", {"zeige_tueren": "false"}),
    ("seite.png", "0,200,225,90,0,90,1300", "o", {}),
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
    platz, fehlt, belegt = pack(p, d)
    write_scad(p, d, platz)
    liste = teile(p, d)
    leer, inhalt = write_stueckliste(p, d, liste, platz)
    write_berechnung(p, d, platz, fehlt, belegt, leer, inhalt)
    print("cad/params.scad, docs/stueckliste.md, docs/berechnung.md geschrieben")
    if fehlt:
        print("WARNUNG – passt nicht in den Stauraum:", ", ".join(i["name"] for i in fehlt))
    if "--no-render" not in sys.argv:
        render()


if __name__ == "__main__":
    main()
