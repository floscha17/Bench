// Sitzbank / Flach- und Schrägbank – parametrisches Modell nach dem Bildentwurf
// Maße kommen aus params.toml (über tools/build.py → params.scad).
// Koordinaten: x = Länge (links→rechts), y = Tiefe (vorne→hinten), z = Höhe.

include <params.scad>

// Ansichtsoptionen (im Customizer oder per -D umschaltbar)
lehne_winkel   = 0;          // 0 = flach, sonst einer der Rastwinkel der Lehne
sitz_winkel    = 0;          // 0 = flach, sonst einer der Sitzwinkel
rolltuer_offen = false;
farbschema     = "eiche";    // "eiche" (Eiche + Cognac-Leder) | "nussbaum" (Nussbaum + schwarzes Leder + Messing)
zeige_polster  = true;
zeige_inhalt   = true;
geist          = false;      // alle Stellungen transparent mit anzeigen
explosion      = 0;          // 0 = zusammengebaut, 1 = Explosionsansicht

$fn = 48;
e = explosion;

nuss = farbschema == "nussbaum";
c_holz   = nuss ? [0.40, 0.27, 0.18] : [0.78, 0.58, 0.36];
c_lamel  = nuss ? [0.37, 0.25, 0.17] : [0.74, 0.54, 0.33];
c_innen  = nuss ? [0.46, 0.33, 0.24] : [0.84, 0.68, 0.48];
c_leder  = nuss ? [0.10, 0.09, 0.09] : [0.60, 0.27, 0.15];
c_metall = nuss ? [0.78, 0.62, 0.32] : [0.11, 0.11, 0.12];
c_bronze = [0.56, 0.41, 0.22];
c_dunkel = [0.09, 0.08, 0.08];
c_hantel = [0.14, 0.14, 0.14];
c_box    = [0.30, 0.33, 0.32];

r_stab = buegel_d / 2;
z_unten = polster_z0 - achse_z;       // Unterseite der Polsterplatte relativ zur Drehachse

// Rechteck mit gerundeten senkrechten Kanten
module rrect(x, y, l, b, r, z0, h) {
    translate([x, y, z0]) hull()
        for (cx = [r, l - r], cy = [r, b - r]) translate([cx, cy, 0]) cylinder(r = r, h = h);
}

module quader(pos, groesse, farbe) {
    translate(pos) color(farbe) cube(groesse);
}

// ---------- Korpus mit gerundeten Ecken ----------

module korpus() {
    // Mantel: Stirnseiten, Eckstollen, Rückwand, Frontleisten oben (Rand) und unten
    color(c_holz) difference() {
        rrect(0, 0, L, D, R, boden_z0, korpus_h);
        rrect(t, t, L - 2 * t, D - 2 * t, R - t, boden_z0 - 1, korpus_h + 2);
        translate([rt_x0, -1, boden_z1]) cube([rt_len, t + 2, innen_h]);
    }
    // Deckel (bildet den Boden der Polsterwanne) und Boden
    color(c_holz) rrect(t, t, L - 2 * t, D - 2 * t, R - t, deckel_z0 + 90 * e, t);
    color(c_holz) rrect(t, t, L - 2 * t, D - 2 * t, R - t, boden_z0 - 30 * e, t);
    // Trennwände (enden vor der hinteren Rolltürbahn) und Fachböden
    for (x = mw_x) quader([x, fach_y0, boden_z1], [ti, fach_tiefe, innen_h], c_innen);
    if (fachboden)
        for (i = [0 : len(fach_x0) - 1])
            quader([fach_x0[i] + 1, fach_y0 + 5, fachboden_z0], [fach_breiten[i] - 2, fach_tiefe - 5, ti], c_innen);
}

module sockel() {
    translate([0, 0, -70 * e]) {
        // Eichenzarge, zurückgesetzt, Ecken gerundet
        color(c_holz) difference() {
            rrect(sockel_einzug, sockel_einzug, L - 2 * sockel_einzug, D - 2 * sockel_einzug,
                  R - sockel_einzug, fuss_h, sockel_h - fuss_h - 0.5);
            rrect(sockel_einzug + 20, sockel_einzug + 20, L - 2 * sockel_einzug - 40, D - 2 * sockel_einzug - 40,
                  R - sockel_einzug - 20, fuss_h - 1, sockel_h);
        }
        // schwarze Füße
        for (p = fuss_pos) translate([p[0], p[1], 0]) color(c_dunkel) cylinder(d = fuss_d, h = fuss_h);
        // Absenkrollen (hochgestellt) und Exzenterwelle
        for (p = rollen_pos) translate([p[0], p[1], fuss_h + 2 + rolle_d / 2]) color(c_dunkel) {
            for (dy = [-11, 1]) translate([0, dy, 0]) rotate([-90, 0, 0]) cylinder(d = rolle_d, h = 10);
            translate([-15, -14, rolle_d / 2]) cube([30, 28, 4]);
        }
        color([0.4, 0.4, 0.4]) translate([rollen_pos[0][0], rollen_pos[0][1], fuss_h + rolle_d + 10])
            rotate([0, 90, 0]) cylinder(d = 16, h = rollen_pos[1][0] - rollen_pos[0][0]);
        // Bronze-Fußhebel vorn rechts
        color(c_bronze) translate([pedal_x, -4, 16]) {
            cube([64, sockel_einzug + 30, 6]);
            translate([0, 0, 6]) cube([64, 5, 6]);
        }
    }
}

// ---------- Rolltür aus Lamellen ----------

module rt_lamelle(h) {
    // gerundete Vorderseite (Kannelur)
    translate([0, 4, 0]) cube([rt_b, rt_dicke - 4, h]);
    translate([rt_b / 2, 4, 0]) scale([1, 8 / rt_b, 1]) cylinder(d = rt_b, h = h, $fn = 24);
}

module rolltuer() {
    h = innen_h - 2;
    schritt = rt_b + rt_fuge;
    color(c_lamel) translate([0, -200 * e, boden_z1 + 1])
        if (!rolltuer_offen) {
            for (i = [0 : rt_n - 1]) translate([rt_x0 + i * schritt, rt_y0, 0]) rt_lamelle(h);
        } else {
            // in der Tasche links nach hinten, dann hinter den Fächern entlang
            n_tasche = floor((fach_tiefe - 20) / schritt);
            for (i = [0 : n_tasche - 1])
                translate([tasche_x0 + 8, fach_y0 + 10 + i * schritt + rt_b, 0]) rotate([0, 0, -90]) rt_lamelle(h);
            for (i = [0 : rt_n - n_tasche - 1])
                translate([tasche_x0 + 30 + i * schritt + rt_b, rt_hinten_y0 + rt_dicke, 0]) rotate([0, 0, 180]) rt_lamelle(h);
        }
}

// ---------- Polster ----------

// Polster in lokalen Koordinaten: u = 0 an der Drehachse (innen), u = laenge außen
module polster_koerper(laenge, alpha = 1) {
    ri = polster_r;
    ra = pad_r_aussen;
    ecken = [[ri, ri, ri], [ri, pad_b - ri, ri], [laenge - ra, ra, ra], [laenge - ra, pad_b - ra, ra]];
    // Trägerplatte mit sichtbarer Eichenkante
    color(c_holz, alpha) hull() for (c = ecken) translate([c[0], c[1], 0]) cylinder(r = c[2], h = polster_platte);
    // Lederpolster mit gerundeter Oberkante
    schaum = polster_h - polster_platte;
    color(c_leder, alpha) hull() for (c = ecken) translate([c[0], c[1], polster_platte]) {
        cylinder(r = c[2] - 1, h = 1);
        for (k = [0 : 3]) {
            w = k * 30;
            translate([0, 0, schaum - polster_r + polster_r * sin(w)])
                cylinder(r = max(c[2] - polster_r + polster_r * cos(w), 0.5), h = 0.5);
        }
    }
}

module gelenkplatte_teil() {
    color(c_metall) rotate([90, 0, 0]) translate([0, 0, -gelenkplatte]) linear_extrude(gelenkplatte)
        hull() {
            circle(r = 11);
            translate([12, z_unten - 4]) square([45, 4]);
        }
}

// Rückenlehne lokal (u nach +x), wird an der Achse gespiegelt, weil sie sich nach links hebt
module lehne_lokal(alpha = 1) {
    translate([0, pad_y0, z_unten]) polster_koerper(lehne_laenge, alpha);
    if (alpha == 1) {
        for (y = rippe_y0)
            translate([20, y, z_unten - rippe_h]) color(c_holz) cube([lehne_rippe_l, rippe_b, rippe_h]);
        for (y = [pad_y0 - gelenkplatte - 0.5, D - pad_y0 + 0.5]) translate([0, y, 0]) gelenkplatte_teil();
        for (y = bein_y0)
            translate([lehne_s - 15, y + (y < D / 2 ? bein_b : -12), z_unten - 14]) color(c_metall) cube([30, 12, 14]);
    }
}

module sitz_lokal(alpha = 1) {
    translate([0, pad_y0, z_unten]) polster_koerper(sitz_laenge, alpha);
    if (alpha == 1)
        for (y = [pad_y0 - gelenkplatte - 0.5, D - pad_y0 + 0.5]) translate([0, y, 0]) gelenkplatte_teil();
}

// Stütze der Lehne: Gelenk A und Querstab N in lokalen Koordinaten [u, z relativ Achse]
function gelenk(a) = [lehne_s * cos(a) - vA * sin(a), lehne_s * sin(a) + vA * cos(a)];
function stab(a) = a == 0
    ? [lehne_s + lehne_l_stuetze, vA]
    : let(A = gelenk(a), dz = A[1] - rast_z)
      [A[0] + sqrt(lehne_l_stuetze * lehne_l_stuetze - dz * dz), rast_z];

module stuetze_lehne(a) {
    A = gelenk(a);
    N = stab(a);
    xa = lehne_achse_x + lehne_dir * A[0];
    xn = lehne_achse_x + lehne_dir * N[0];
    color(c_metall) {
        for (y = bein_y0) hull() {
            translate([xa, y, achse_z + A[1]]) rotate([-90, 0, 0]) cylinder(d = bein_t, h = bein_b);
            translate([xn, y, achse_z + N[1]]) rotate([-90, 0, 0]) cylinder(d = bein_t, h = bein_b);
        }
        translate([xn, stab_y0, achse_z + N[1]]) rotate([-90, 0, 0]) cylinder(d = buegel_d, h = stab_l);
    }
}

// Klappbügel unter dem Sitz: je Winkel einer, ineinander geschachtelt.
// Der Bügel des eingestellten Winkels steht senkrecht, die anderen liegen flach in der Wanne.
module sitzbuegel(a) {
    n = len(sitz_stufen);
    for (i = [0 : n - 1]) {
        u = sitz_stufen[i][0];
        h = sitz_stufen[i][1];
        y0 = bein_y0[0] + 2 + (n - 1 - i) * 12;
        y1 = bein_y0[1] + bein_b - 2 - (n - 1 - i) * 12;
        steht = a == sitz_winkel_liste[i];
        // Beine Flachstahl 30 × 8 (8 mm in Längsrichtung, damit der Bügel umgeklappt flach liegt)
        color(c_metall) translate([sitz_achse_x + u, 0, deckel_z1 + (steht ? 0 : 8)]) rotate([0, steht ? 0 : -90, 0]) {
            for (y = [y0, y1 - 30]) translate([-8, y, 0]) cube([8, 30, h]);
            translate([-8, y0, h - 8]) cube([8, y1 - y0, 8]);
        }
    }
}

module leisten() {
    translate([0, 0, 150 * e]) color(c_dunkel) {
        for (y = leiste_y0) {
            difference() {
                translate([lehne_leiste_x0, y, deckel_z1]) cube([lehne_leiste_x1 - lehne_leiste_x0, leiste_b, rand]);
                for (n = lehne_rasten)
                    translate([lehne_achse_x + lehne_dir * n, y - 1, polster_z0 - rast_tiefe + r_stab])
                        rotate([-90, 0, 0]) cylinder(d = buegel_d + 1, h = leiste_b + 2);
                translate([lehne_achse_x + lehne_dir * lehne_park - r_stab - 0.5, y - 1, polster_z0 - park_tiefe])
                    cube([buegel_d + 1, leiste_b + 2, park_tiefe + 1]);
            }
            translate([sitz_leiste_x0, y, deckel_z1]) cube([sitz_leiste_x1 - sitz_leiste_x0, leiste_b, rand]);
        }
    }
}

module gelenkplatten_korpus() {
    // je eine Platte vorn und hinten am Rand, trägt beide Achsen
    for (y = [t + 0.5, D - t - 0.5 - gelenkplatte])
        translate([0, y + gelenkplatte, achse_z + 200 * e]) color(c_metall) rotate([90, 0, 0])
            linear_extrude(gelenkplatte) hull() {
                translate([lehne_achse_x, 0]) circle(r = 11);
                translate([sitz_achse_x, 0]) circle(r = 11);
                translate([lehne_achse_x - 14, deckel_z1 - achse_z]) square([sitz_achse_x - lehne_achse_x + 28, 6]);
            }
}

module lehne(a, alpha = 1) {
    translate([lehne_achse_x, 0, achse_z + 260 * e]) mirror([1, 0, 0]) rotate([0, -a, 0]) lehne_lokal(alpha);
}

module sitz(a, alpha = 1) {
    translate([sitz_achse_x, 0, achse_z + 260 * e]) rotate([0, -a, 0]) sitz_lokal(alpha);
}

// ---------- Inhalt ----------

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

module inhalt_zeichnen() {
    for (it = inhalt) {
        typ = it[0]; x = it[1]; y = it[2]; z = it[3];
        b = it[4]; h = it[5]; tf = it[6]; kopf = it[7]; kopf_l = it[8];
        translate([x, y, z])
            if (typ == "khr") {
                // schwarze Ablage unter den Köpfen
                color(c_dunkel) for (yy = [0, tf - kopf_l]) translate([-4, yy, 0]) cube([b + 8, kopf_l, ablage_h]);
                translate([0, 0, ablage_h]) {
                    hantel_rund(kopf, kopf_l, tf);
                    translate([kopf + abstand, 0, 0]) hantel_rund(kopf, kopf_l, tf);
                }
            } else {
                color(c_box) cube([b, tf, h]);
            }
    }
}

// ---------- Zusammenbau ----------

korpus();
sockel();
rolltuer();
leisten();
gelenkplatten_korpus();
translate([0, 0, 260 * e]) stuetze_lehne(lehne_winkel);
translate([0, 0, 150 * e]) sitzbuegel(sitz_winkel);
if (zeige_polster) {
    lehne(lehne_winkel);
    sitz(sitz_winkel);
    if (geist) {
        for (a = concat([0], lehne_winkel_liste)) if (a != lehne_winkel) lehne(a, 0.18);
        for (a = concat([0], sitz_winkel_liste)) if (a != sitz_winkel) sitz(a, 0.18);
    }
}
if (zeige_inhalt) inhalt_zeichnen();
