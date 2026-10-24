// Sitzbank / Flach- und Schrägbank – parametrisches Modell
// Maße kommen aus params.toml (über tools/build.py → params.scad).
// Koordinaten: x = Länge (links→rechts), y = Tiefe (vorne→hinten), z = Höhe.

include <params.scad>

// Ansichtsoptionen (im Customizer oder per -D umschaltbar)
lehne_winkel  = 0;          // 0 = flach, sonst einer der Rastwinkel
farbschema    = "eiche";    // "eiche" (Eiche natur + Cognac-Leder) | "nussbaum" (Nussbaum + schwarzes Leder + Messing)
zeige_tueren  = true;
zeige_polster = true;
zeige_inhalt  = true;
geist         = false;      // alle Raststellungen transparent mit anzeigen
explosion     = 0;          // 0 = zusammengebaut, 1 = Explosionsansicht

$fn = 40;
e = explosion;

nuss = farbschema == "nussbaum";
c_holz   = nuss ? [0.40, 0.27, 0.18] : [0.80, 0.65, 0.46];
c_lamel  = nuss ? [0.37, 0.25, 0.17] : [0.76, 0.61, 0.42];
c_innen  = nuss ? [0.46, 0.33, 0.24] : [0.86, 0.74, 0.56];
c_leder  = nuss ? [0.10, 0.09, 0.09] : [0.55, 0.31, 0.16];
c_metall = nuss ? [0.80, 0.63, 0.32] : [0.13, 0.13, 0.14];
c_dunkel = [0.09, 0.08, 0.08];
c_hantel = [0.14, 0.14, 0.14];
c_box    = [0.30, 0.33, 0.32];
c_rolle  = [0.08, 0.08, 0.08];

r_stab = buegel_d / 2;

module quader(pos, groesse, farbe) {
    translate(pos) color(farbe) cube(groesse);
}

// ---------- Korpus ----------

module korpus() {
    // Gehrungskasten aus Eiche: Deckel, Boden, Seitenwangen
    quader([0, 0, deckel_z0 + 90 * e], [L, D, t], c_holz);
    quader([0, 0, boden_z0 - 30 * e], [L, D, t], c_holz);
    quader([-140 * e, 0, boden_z0], [t, D, korpus_h], c_holz);
    quader([L - t + 140 * e, 0, boden_z0], [t, D, korpus_h], c_holz);
    // Innenleben
    quader([t, rueck_y0 + 120 * e, boden_z1], [innen_l, tr, innen_h], c_innen);
    if (n_mw > 0) for (i = [1 : n_mw])
        quader([fach_x0[i] - ti, fach_y0, boden_z1], [ti, fach_tiefe, innen_h], c_innen);
    if (fachboden)
        for (x = fach_x0)
            quader([x + 1, fach_y0 + 5, fachboden_z0], [fach_breite - 2, fach_tiefe - 5, ti], c_innen);
}

module sockel() {
    translate([0, 0, -70 * e]) color(c_dunkel) difference() {
        translate([sockel_einzug, sockel_einzug, 0])
            cube([L - 2 * sockel_einzug, D - 2 * sockel_einzug, sockel_h - 0.5]);
        translate([sockel_einzug + t, sockel_einzug + t, -1])
            cube([L - 2 * sockel_einzug - 2 * t, D - 2 * sockel_einzug - 2 * t, sockel_h + 2]);
    }
}

// Rollen verdeckt unter dem hinteren Überstand (Bettseite), rollen quer zur Bank
module rollen() {
    for (x = rolle_x)
        translate([x - rolle_b / 2, D - sockel_einzug / 2, rolle_d / 2 + rolle_luft - 70 * e]) {
            rotate([0, 90, 0]) color(c_rolle) cylinder(d = rolle_d, h = rolle_b);
            color([0.5, 0.5, 0.5]) translate([-3, -12, rolle_d / 2 - 2]) cube([rolle_b + 6, 24, 4]);
        }
}

// ---------- Türen aus Lamellen ----------

module lamelle(h) {
    // Vorderkanten gerundet
    hull() for (x = [3, lamelle_b - 3])
        translate([x, 3, 0]) cylinder(r = 3, h = h, $fn = 16);
    translate([0, 3, 0]) cube([lamelle_b, lamelle_dicke - 3, h]);
}

module tuer() {
    h = tuer_h;
    color(c_lamel) for (k = [0 : n_lamellen - 1])
        translate([k * (lamelle_b + lamelle_fuge), 0, 0]) lamelle(h);
    // verdeckte Traversen hinter den Lamellen
    color(c_dunkel) for (z = [20, h - 60])
        translate([0, lamelle_dicke, z]) cube([tuer_l, traverse_dicke, 40]);
}

module tueren() {
    for (i = [0 : len(tuer_x0) - 1])
        translate([tuer_x0[i], tuer_y0[i % 2] - 220 * e, tuer_z0]) tuer();
}

// ---------- Polster ----------

module polster(laenge, alpha = 1) {
    // Lederpolster: Trägerplatte ist umpolstert, Kanten gerundet
    r = polster_r;
    color(c_leder, alpha) hull() {
        for (x = [r, laenge - r], y = [r, pad_b - r]) {
            translate([x, y, polster_h - r]) sphere(r = r);
            translate([x, y, 3]) sphere(r = 3);
        }
    }
}

module sitz() {
    translate([sitz_x0, pad_y0, polster_z0 + 260 * e]) polster(sitz_x1 - sitz_x0);
    // schwarzer Distanzrahmen unter dem Sitz (Schattenfuge)
    translate([sitz_x0 + 25, pad_y0 + 25, deckel_z1 + 150 * e]) color(c_dunkel) difference() {
        cube([sitz_x1 - sitz_x0 - 50, pad_b - 50, schattenfuge]);
        translate([20, 20, -1]) cube([sitz_x1 - sitz_x0 - 90, pad_b - 90, schattenfuge + 2]);
    }
}

// Lehne in eigenen Koordinaten (Ursprung = Drehachse), flach
module lehne_lokal(alpha = 1) {
    z_unten = polster_z0 - achse_z;
    translate([0, pad_y0, z_unten]) polster(lehne_l, alpha);
    if (alpha == 1) {
        // Eichenrippen unter der Lehnenplatte
        for (y = rippe_y0)
            translate([20, y, z_unten - rippe_h]) color(c_holz) cube([rippe_l, rippe_b, rippe_h]);
        // Gelenkplatten der Lehne (innen), vorne und hinten
        for (y = [pad_y0 - gelenkplatte - 1.5, D - pad_y0 + 1.5])
            translate([0, y, 0]) gelenkplatte_lehne();
        // Lagerböcke der Stütze
        for (y = bein_y0)
            translate([stuetze_s - 15, y + (y < D / 2 ? bein_b : -12), z_unten - 14])
                color(c_metall) cube([30, 12, 14]);
    }
}

module gelenkplatte_lehne() {
    z_unten = polster_z0 - achse_z;
    color(c_metall) rotate([90, 0, 0]) translate([0, 0, -gelenkplatte]) linear_extrude(gelenkplatte)
        hull() {
            circle(r = 11);
            translate([12, z_unten - 4]) square([45, 4]);
        }
}

module gelenkplatten_korpus() {
    // äußere Platten, mit Fuß unter dem Sitz verschraubt
    for (y = [pad_y0 - 2 * gelenkplatte - 3, D - pad_y0 + 3 + gelenkplatte])
        translate([achse_x, y, achse_z + 200 * e]) color(c_metall)
            rotate([90, 0, 0]) translate([0, 0, -gelenkplatte]) linear_extrude(gelenkplatte)
                hull() {
                    circle(r = 11);
                    translate([-30, deckel_z1 - achse_z]) square([38, 6]);
                }
    // Bolzenköpfe
    for (y = [pad_y0 - 2 * gelenkplatte - 5, D - pad_y0 + 3 + 2 * gelenkplatte])
        translate([achse_x, y, achse_z + 200 * e]) rotate([-90, 0, 0])
            color(nuss ? c_metall : [0.72, 0.58, 0.30]) cylinder(d = 16, h = 2);
}

// Pose der Stütze für einen Winkel: [Gelenk A, Mitte Querstab N] in globalen x/z
function gelenk(a) = [achse_x + stuetze_s * cos(a) - vA * sin(a),
                      achse_z + stuetze_s * sin(a) + vA * cos(a)];
function stab(a) = a == 0
    ? [achse_x + stuetze_s + stuetze_l, achse_z + vA]
    : let(A = gelenk(a), dz = A[1] - (achse_z + rast_z))
      [A[0] + sqrt(stuetze_l * stuetze_l - dz * dz), achse_z + rast_z];

module stuetze(a) {
    A = gelenk(a);
    N = stab(a);
    color(c_metall) {
        for (y = bein_y0) hull() {
            translate([A[0], y, A[1]]) rotate([-90, 0, 0]) cylinder(d = bein_t, h = bein_b);
            translate([N[0], y, N[1]]) rotate([-90, 0, 0]) cylinder(d = bein_t, h = bein_b);
        }
        translate([N[0], stab_y0, N[1]]) rotate([-90, 0, 0]) cylinder(d = buegel_d, h = stab_l);
    }
}

module rastleisten() {
    translate([0, 0, 150 * e]) color(c_dunkel) for (y = leiste_y0) difference() {
        translate([leiste_x0, y, deckel_z1]) cube([leiste_x1 - leiste_x0, leiste_b, schattenfuge]);
        for (n = rasten)
            translate([achse_x + n, y - 1, polster_z0 - rast_tiefe + r_stab])
                rotate([-90, 0, 0]) cylinder(d = buegel_d + 1, h = leiste_b + 2);
        // Parkrast: Stab liegt versenkt, die Lehne liegt flach auf
        translate([achse_x + park, y - 1, polster_z0 - park_tiefe + r_stab])
            rotate([-90, 0, 0]) cylinder(d = buegel_d + 1, h = leiste_b + 2);
        translate([achse_x + park - r_stab - 0.5, y - 1, polster_z0 - park_tiefe + r_stab])
            cube([buegel_d + 1, leiste_b + 2, park_tiefe]);
    }
}

module lehne(a) {
    translate([achse_x, 0, achse_z + 260 * e]) rotate([0, -a, 0]) lehne_lokal();
    translate([0, 0, 260 * e]) stuetze(a);
}

// ---------- Inhalt ----------

// selbstgebaute Hantel: runde Stahlköpfe mit Abflachung, Eichengriff; liegt auf der Abflachung
module hantel_rund(kopf, kopf_l, laenge) {
    zc = kopf / 2 - abflachung;
    difference() {
        for (y = [0, laenge - kopf_l])
            translate([kopf / 2, y, zc]) rotate([-90, 0, 0])
                color(c_hantel) cylinder(d = kopf, h = kopf_l, $fn = 48);
        translate([-1, -1, -kopf]) cube([kopf + 2, laenge + 2, kopf]);
    }
    translate([kopf / 2, kopf_l, zc]) rotate([-90, 0, 0])
        color(c_holz) cylinder(d = griff_d, h = laenge - 2 * kopf_l, $fn = 32);
}

module kurzhantel(kopf, laenge) {
    kl = kopf * 0.42;
    for (y = [0, laenge - kl])
        translate([kopf / 2, y, kopf / 2]) rotate([-90, 0, 0])
            color(c_hantel) cylinder(d = kopf / cos(30), h = kl, $fn = 6);
    translate([kopf / 2, kl, kopf / 2]) rotate([-90, 0, 0])
        color([0.7, 0.7, 0.7]) cylinder(d = 32, h = laenge - 2 * kl);
}

module inhalt_zeichnen() {
    for (it = inhalt) {
        typ = it[0]; x = it[1]; y = it[2]; z = it[3];
        b = it[4]; h = it[5]; tf = it[6]; kopf = it[7]; kopf_l = it[8];
        translate([x, y, z])
            if (typ == "khr") {
                hantel_rund(kopf, kopf_l, tf);
                translate([kopf + abstand, 0, 0]) hantel_rund(kopf, kopf_l, tf);
            } else if (typ == "kh") {
                kurzhantel(kopf, tf);
                translate([kopf + abstand, 0, 0]) kurzhantel(kopf, tf);
            } else {
                color(c_box) cube([b, tf, h]);
            }
    }
}

// ---------- Zusammenbau ----------

korpus();
sockel();
if (rollen) rollen();
if (zeige_tueren) tueren();
rastleisten();
gelenkplatten_korpus();
if (zeige_polster) {
    sitz();
    lehne(lehne_winkel);
    if (geist)
        for (a = concat([0], winkel)) if (a != lehne_winkel)
            translate([achse_x, 0, achse_z]) rotate([0, -a, 0]) lehne_lokal(0.18);
}
if (zeige_inhalt) inhalt_zeichnen();
