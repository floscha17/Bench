// Sitzbank / Trainingsbank – parametrisches Modell
// Maße kommen aus params.toml (über tools/build.py → params.scad).
// Koordinaten: x = Länge (links→rechts), y = Tiefe (vorne→hinten), z = Höhe.

include <params.scad>

// Ansichtsoptionen (im Customizer oder per -D umschaltbar)
zeige_tueren  = true;
zeige_polster = true;
zeige_inhalt  = true;
explosion     = 0;     // 0 = zusammengebaut, 1 = Explosionsansicht

$fn = 48;
e = explosion;

c_holz   = [0.86, 0.74, 0.56];
c_kante  = [0.80, 0.66, 0.48];
c_buche  = [0.78, 0.58, 0.40];
c_tuer   = [0.83, 0.70, 0.52];
c_polst  = [0.26, 0.24, 0.23];
c_hantel = [0.15, 0.15, 0.15];
c_box    = [0.45, 0.55, 0.50];
c_rolle  = [0.10, 0.10, 0.10];

module platte(pos, groesse, farbe = c_holz) {
    translate(pos) color(farbe) cube(groesse);
}

// Langloch in der x-Ebene (für das Griffloch)
module langloch_x(b, h, dicke) {
    hull() for (dy = [h / 2, b - h / 2])
        translate([0, dy, h / 2]) rotate([0, 90, 0]) cylinder(d = h, h = dicke);
}

module seitenwange(links) {
    color(c_holz) difference() {
        cube([t, D, seite_h]);
        // Fußausschnitt mit gerundeten Ecken
        hull() {
            for (y = [fuss_b + 10, D - fuss_b - 10])
                translate([-1, y, fuss_h - 10]) rotate([0, 90, 0]) cylinder(r = 10, h = t + 2);
            translate([-1, fuss_b, -1]) cube([t + 2, D - 2 * fuss_b, 1]);
        }
        if (links)
            translate([-1, (D - griff_b) / 2, seite_h - griff_oben - griff_h])
                langloch_x(griff_b, griff_h, t + 2);
    }
}

module korpus() {
    // Seitenwangen
    translate([-150 * e, 0, 0]) seitenwange(true);
    translate([L - t + 150 * e, 0, 0]) seitenwange(false);
    // Deckel
    platte([0, 0, deckel_z0 + 120 * e], [L, D, t]);
    // Boden mit Laufnuten
    color(c_holz) translate([t, 0, boden_z0 - 40 * e]) difference() {
        cube([innen_l, D, t]);
        for (y = spur_y0) translate([-1, y, t - nut_unten]) cube([innen_l + 2, nut_breite, nut_unten + 1]);
    }
    // Rückwand
    platte([t, rueck_y0 + 120 * e, boden_z1], [innen_l, t, innen_h]);
    // Sockelblenden
    platte([t, sockel_versatz - 60 * e, -60 * e], [innen_l, t, fuss_h], c_kante);
    platte([t, D - t + 60 * e, -60 * e], [innen_l, t, fuss_h], c_kante);
    // Mittelwände
    if (n_mw > 0) for (i = [1 : n_mw])
        platte([fach_x0[i] - t, fach_y0, boden_z1 + 40 * e], [t, fach_tiefe, innen_h]);
    // Fachböden
    if (fachboden)
        for (x = fach_x0)
            platte([x + 1, fach_y0 + 5, fachboden_z0 + 70 * e], [fach_breite - 2, fach_tiefe - 5, t]);
    // Führungsleiste (Buche) mit zwei Nuten für die Türen
    color(c_buche) translate([t, -80 * e, leiste_z0 + 60 * e]) difference() {
        cube([innen_l, leiste_t, leiste_h]);
        for (y = spur_y0) translate([-1, y, -1]) cube([innen_l + 2, nut_breite, nut_oben + 1]);
    }
}

module tuer(i) {
    n_schlitz = floor((tuer_l - 2 * schlitz_rand) / schlitz_abst) + 1;
    x_start = (tuer_l - (n_schlitz - 1) * schlitz_abst) / 2;
    color(c_tuer) difference() {
        cube([tuer_l, tt, tuer_h]);
        for (k = [0 : n_schlitz - 1])
            hull() for (z = [schlitz_rand + schlitz_b / 2, tuer_h - schlitz_rand - schlitz_b / 2])
                translate([x_start + k * schlitz_abst, -1, z]) rotate([-90, 0, 0])
                    cylinder(d = schlitz_b, h = tt + 2);
    }
}

module tueren() {
    for (i = [0 : len(tuer_x0) - 1])
        translate([tuer_x0[i], tuer_y0[i % 2] - 200 * e, tuer_z0]) tuer(i);
}

module polster() {
    translate([0, 0, deckel_z1 + 260 * e]) {
        platte([0, 0, 0], [L, D, polster_platte]);
        color(c_polst) hull() {
            translate([0, 0, polster_platte]) cube([L, D, 1]);
            for (x = [polster_r, L - polster_r], y = [polster_r, D - polster_r])
                translate([x, y, polster_platte + polster_schaum - polster_r]) sphere(r = polster_r);
        }
    }
}

module rollen() {
    // Rollen vor der rechten Stirnseite, im Bereich der Füße
    for (y = [fuss_b / 2 - rolle_b / 2, D - fuss_b / 2 - rolle_b / 2]) {
        translate([L + rolle_d / 2 + 2 + 150 * e, y, rolle_d / 2 + rolle_luft]) rotate([-90, 0, 0]) {
            color(c_rolle) cylinder(d = rolle_d, h = rolle_b);
            color([0.6, 0.6, 0.6]) cylinder(d = 8, h = rolle_b + 4, center = false);
        }
        // Halter
        color([0.6, 0.6, 0.6])
            translate([L + 150 * e, y - 3, rolle_luft + rolle_d / 2 - 6])
                cube([rolle_d / 2 + 6, 3, 12]);
    }
}

module kurzhantel(kopf, laenge) {
    kl = kopf * 0.42;          // Kopflänge
    // Sechskantköpfe, liegend auf einer Schlüsselfläche
    for (y = [0, laenge - kl])
        translate([kopf / 2, y, kopf / 2]) rotate([-90, 0, 0])
            color(c_hantel) cylinder(d = kopf / cos(30), h = kl, $fn = 6);
    translate([kopf / 2, kl, kopf / 2]) rotate([-90, 0, 0])
        color([0.7, 0.7, 0.7]) cylinder(d = 32, h = laenge - 2 * kl);
}

module inhalt_zeichnen() {
    for (it = inhalt) {
        typ = it[0]; x = it[1]; y = it[2]; z = it[3];
        b = it[4]; h = it[5]; tf = it[6]; kopf = it[7];
        translate([x, y, z + (z > fachboden_z0 ? 70 * e : -40 * e)])
            if (typ == "kh") {
                kurzhantel(kopf, tf);
                translate([kopf + abstand, 0, 0]) kurzhantel(kopf, tf);
            } else {
                color(c_box) cube([b, tf, h]);
            }
    }
}

korpus();
if (zeige_tueren) tueren();
if (zeige_polster) polster();
if (rollen) rollen();
if (zeige_inhalt) inhalt_zeichnen();
