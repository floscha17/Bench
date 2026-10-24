// Wohnbank mit Trainingsfunktion – parametrisches Modell nach Studio-Vorentwurf V01
// Maße kommen aus params.toml (über tools/build.py → params.scad).
// Koordinaten: x = Länge (links→rechts), y = Tiefe (vorne→hinten), z = Höhe.
// Tragstruktur: innenliegender Stahlrahmen; das Holz ist Verkleidung.

include <params.scad>

// Ansichtsoptionen (im Customizer oder per -D umschaltbar)
lehne_winkel   = 0;          // 0 = flach, sonst einer der Arbeitswinkel der Lehne
sitz_winkel    = 0;          // 0 = flach, sonst einer der Sitzwinkel
rolltuer_offen = false;
farbschema     = "eiche";    // "eiche" | "nussbaum"
zeige_holz     = true;       // false: nur Stahlrahmen, Mechanik und Polster (Tragwerk)
zeige_polster  = true;
zeige_inhalt   = true;
geist          = false;      // alle Stellungen transparent mit anzeigen
explosion      = 0;          // 0 = zusammengebaut, 1 = Explosionsansicht

$fn = 40;
e = explosion;

nuss = farbschema == "nussbaum";
c_holz   = nuss ? [0.40, 0.27, 0.18] : [0.78, 0.58, 0.36];
c_lamel  = nuss ? [0.37, 0.25, 0.17] : [0.74, 0.54, 0.33];
c_innen  = nuss ? [0.46, 0.33, 0.24] : [0.84, 0.68, 0.48];
c_leder  = nuss ? [0.10, 0.09, 0.09] : [0.60, 0.27, 0.15];
c_stahl  = [0.16, 0.16, 0.17];
c_bronze = [0.56, 0.41, 0.22];
c_dunkel = [0.09, 0.08, 0.08];
c_hantel = [0.14, 0.14, 0.14];
c_box    = [0.30, 0.33, 0.32];

z_unten = polster_z0 - achse_z;       // Unterseite der Polsterplatte relativ zur Drehachse

module rrect(x, y, l, b, r, z0, h) {
    translate([x, y, z0]) hull()
        for (cx = [r, l - r], cy = [r, b - r]) translate([cx, cy, 0]) cylinder(r = r, h = h);
}

module quader(pos, groesse, farbe) {
    translate(pos) color(farbe) cube(groesse);
}

// ---------- Holzverkleidung ----------

module verkleidung() {
    color(c_holz) difference() {
        rrect(0, 0, L, D, R, boden_z0, korpus_h);
        rrect(t, t, L - 2 * t, D - 2 * t, R - t, boden_z0 - 1, korpus_h + 2);
        translate([rt_x0, -1, boden_z1]) cube([rt_len, t + 2, innen_h]);
    }
    // Wannenboden und Boden
    color(c_holz) rrect(t, t, L - 2 * t, D - 2 * t, R - t, deckel_z0 + 90 * e, t);
    color(c_holz) rrect(t, t, L - 2 * t, D - 2 * t, R - t, boden_z0 - 30 * e, t);
    // Trennwände (nicht tragend) und Fachboden im Zubehörbereich
    for (x = mw_x) quader([x, fach_y0, boden_z1], [ti, fach_tiefe, innen_h], c_innen);
    quader([fach_x0[1] + 1, fach_y0 + 5, ebene_z0], [fach_breiten[1] - 2, fach_tiefe - 5, ti], c_innen);
    // Sockelzarge
    translate([0, 0, -70 * e]) color(c_holz) difference() {
        rrect(sockel_einzug, sockel_einzug, L - 2 * sockel_einzug, D - 2 * sockel_einzug,
              R - sockel_einzug, fuss_h, sockel_h - fuss_h - 0.5);
        rrect(sockel_einzug + 20, sockel_einzug + 20, L - 2 * sockel_einzug - 40, D - 2 * sockel_einzug - 40,
              R - sockel_einzug - 20, fuss_h - 1, sockel_h);
        translate([pedal_x - 5, sockel_einzug - 1, fuss_h + 8]) cube([74, 22, 22]);   // Pedalausschnitt
    }
}

module rt_lamelle(h) {
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
            n_tasche = floor((fach_tiefe - 20) / schritt);
            for (i = [0 : n_tasche - 1])
                translate([tasche_x0 + 8, fach_y0 + 10 + i * schritt + rt_b, 0]) rotate([0, 0, -90]) rt_lamelle(h);
            for (i = [0 : rt_n - n_tasche - 1])
                translate([tasche_x0 + 30 + i * schritt + rt_b, rt_hinten_y0 + rt_dicke, 0]) rotate([0, 0, 180]) rt_lamelle(h);
        }
}

// ---------- Innenrahmen (Stahl) ----------

module rahmen() {
    color(c_stahl) {
        // Längsrohre in der Wanne: tragen Polster, Gelenke und Gleitschienen
        for (y = rohr_y0) translate([t + 3, y, deckel_z1]) cube([L - 2 * t - 6, rohr_b, rohr_h]);
        // Stützen bis zu den Füßen, unten Längs- und oben/unten Querrohre
        for (x = stuetze_x, y = stuetze_y) translate([x, y, fuss_h + 25]) cube([stuetze_q, stuetze_q, deckel_z1 - fuss_h - 25]);
        for (y = stuetze_y) translate([stuetze_x[0], y, fuss_h + 25]) cube([stuetze_x[2] + stuetze_q - stuetze_x[0], stuetze_q, stuetze_q]);
        for (x = stuetze_x)
            translate([x, stuetze_y[0], deckel_z0 - stuetze_q]) cube([stuetze_q, stuetze_y[1] - stuetze_y[0], stuetze_q]);
        // Hantel-Traversen (Flachstahl hochkant) unter den Griffenden, je Ebene 2
        for (z = [boden_z1, ebene_z0], y = traverse_y)
            translate([stuetze_x[0] + stuetze_q, y - traverse_t / 2, z]) cube([stuetze_x[1] - stuetze_x[0] - stuetze_q, traverse_t, traverse_b]);
    }
    // Stellfüße unter den Eckstützen
    for (p = fuss_pos) translate([p[0], p[1], 0]) color(c_dunkel) {
        cylinder(d = fuss_d, h = fuss_h);
        cylinder(d = 12, h = fuss_h + 25);
    }
}

// mittlere y-Lage der Hantel-Griffenden (alle Hanteln haben dieselbe Grifflänge)
traverse_y = [fach_y0 + fach_tiefe / 2 - 125 / 2 + 15, fach_y0 + fach_tiefe / 2 + 125 / 2 - 15];

// ---------- Fahrwerk ----------

module fahrwerk() {
    translate([0, 0, -70 * e]) {
        color([0.35, 0.35, 0.36]) {
            // geführter Rollenrahmen
            for (y = [rollen_pos[0][1], rollen_pos[2][1]])
                translate([rollen_pos[0][0] - 15, y - 10, rolle_d + 10]) cube([rollen_pos[1][0] - rollen_pos[0][0] + 30, 20, 8]);
            for (x = [rollen_pos[0][0], rollen_pos[1][0]])
                translate([x - 10, rollen_pos[0][1] - 10, rolle_d + 10]) cube([20, rollen_pos[2][1] - rollen_pos[0][1] + 20, 8]);
            // zwei Exzenterwellen, quer, mit Koppelstange
            for (x = [rollen_pos[0][0] + 50, rollen_pos[1][0] - 50])
                translate([x, rollen_pos[0][1], rolle_d + 2]) rotate([-90, 0, 0]) cylinder(d = 14, h = rollen_pos[2][1] - rollen_pos[0][1]);
            translate([rollen_pos[0][0] + 50, rollen_pos[0][1] + 20, rolle_d - 2]) cube([rollen_pos[1][0] - rollen_pos[0][0] - 100, 8, 8]);
        }
        // Lenkrollen, hochgestellt (Bodenfreiheit)
        for (p = rollen_pos) translate([p[0], p[1], 4]) color(c_dunkel) {
            translate([0, -9, rolle_d / 2]) rotate([-90, 0, 0]) cylinder(d = rolle_d, h = 18);
            translate([-12, -12, rolle_d]) cube([24, 24, 6]);
        }
        // Bronze-Fußpedal, versenkt rechts im Sockel
        color(c_bronze) translate([pedal_x, sockel_einzug - 2, fuss_h + 14]) {
            cube([64, 40, 6]);
            translate([0, 0, 6]) cube([64, 4, 4]);
        }
    }
}

// ---------- Polster und Mechanik ----------

module polster_koerper(laenge, alpha = 1) {
    ri = polster_r;
    ra = pad_r_aussen;
    ecken = [[ri, ri, ri], [ri, pad_b - ri, ri], [laenge - ra, ra, ra], [laenge - ra, pad_b - ra, ra]];
    color(c_holz, alpha) hull() for (c = ecken) translate([c[0], c[1], 0]) cylinder(r = c[2], h = polster_platte);
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

module gelenklasche() {
    color(c_stahl) rotate([90, 0, 0]) translate([0, 0, -gelenkplatte]) linear_extrude(gelenkplatte)
        hull() {
            circle(r = 10);
            translate([achs_versatz + 10, z_unten - 4]) square([45, 4]);
        }
}

// Klappteil lokal: u = 0 an der Achse, nach +x
module teil_lokal(laenge, rippe_l, s, alpha = 1) {
    translate([achs_versatz, pad_y0, z_unten]) polster_koerper(laenge, alpha);
    if (alpha == 1) {
        if (rippe_l > 0)
            for (y = rippe_y0) translate([achs_versatz + 20, y, z_unten - rippe_h]) color(c_holz) cube([rippe_l, rippe_b, rippe_h]);
        for (y = [pad_y0 - gelenkplatte - 0.5, D - pad_y0 + 0.5]) translate([0, y, 0]) gelenklasche();
        for (y = bein_y0)
            translate([s - 15, y + (y < D / 2 ? bein_b : -12), z_unten - 12]) color(c_stahl) cube([30, 12, 12]);
    }
}

module klappteil(achse_x, richtung, laenge, rippe_l, s, a, alpha = 1) {
    translate([achse_x, 0, achse_z + 260 * e])
        if (richtung < 0) mirror([1, 0, 0]) rotate([0, -a, 0]) teil_lokal(laenge, rippe_l, s, alpha);
        else rotate([0, -a, 0]) teil_lokal(laenge, rippe_l, s, alpha);
}

// Gleitstütze: Gelenk A unter dem Polster, Gleitschuh N in der C-Schiene
function gelenk(s, a) = [s * cos(a) - vA * sin(a), s * sin(a) + vA * cos(a)];
function fuss(s, l, a) = let(A = gelenk(s, a), dz = A[1] - schiene_z) [A[0] + sqrt(l * l - dz * dz), schiene_z];

module gleitstuetze(achse_x, richtung, s, l, a) {
    A = gelenk(s, a);
    N = fuss(s, l, a);
    xa = achse_x + richtung * A[0];
    xn = achse_x + richtung * N[0];
    color(c_stahl) {
        for (y = bein_y0) {
            hull() {
                translate([xa, y, achse_z + A[1]]) rotate([-90, 0, 0]) cylinder(d = bein_t, h = bein_b);
                translate([xn, y, achse_z + N[1]]) rotate([-90, 0, 0]) cylinder(d = bein_t, h = bein_b);
            }
            translate([xn - 15, y - 2, deckel_z1 + 2]) cube([30, bein_b + 4, schiene_h - 2]);   // Gleitschuh
        }
        // Steg nahe am Fuß
        xs = xn + (xa - xn) * 0.15;
        zs = achse_z + N[1] + (A[1] - N[1]) * 0.15;
        translate([xs, stab_y0, zs]) rotate([-90, 0, 0]) cylinder(d = 12, h = stab_l);
    }
    // Zugknopf des Indexbolzens
    color(c_bronze) translate([xn, bein_y0[0] - 14, deckel_z1 + schiene_h / 2]) rotate([-90, 0, 0]) cylinder(d = 12, h = 10);
}

module gleitschienen(achse_x, richtung, x0, x1, loecher) {
    translate([0, 0, 150 * e]) for (y = bein_y0) {
        color(c_stahl) difference() {
            translate([x0, y + bein_b / 2 - schiene_b / 2, deckel_z1]) cube([x1 - x0, schiene_b, schiene_h]);
            translate([x0 - 1, y - 2, deckel_z1 + 2]) cube([x1 - x0 + 2, bein_b + 4, schiene_h]);
        }
        for (n = loecher)
            translate([achse_x + richtung * n, y - 4, deckel_z1 + schiene_h / 2]) rotate([-90, 0, 0])
                color([0.85, 0.85, 0.85]) cylinder(d = bolzen_d, h = 3);
    }
}

module gelenkkonsolen() {
    // auf den Längsrohren, tragen beide Achsen
    for (y = [t + 0.5, D - t - 0.5 - gelenkplatte])
        translate([0, y + gelenkplatte, achse_z + 200 * e]) color(c_stahl) rotate([90, 0, 0])
            linear_extrude(gelenkplatte) hull() {
                translate([lehne_achse_x, 0]) circle(r = 10);
                translate([lehne_achse_x - konsole_b / 2, deckel_z1 + rohr_h - achse_z]) square([konsole_b, 6]);
            }
}

// ---------- Hanteln in Einzelaufnahmen ----------

module hantel_rund(kopf, kopf_l, laenge) {
    zc = kopf / 2;
    for (y = [0, laenge - kopf_l])
        difference() {
            translate([kopf / 2, y, zc]) rotate([-90, 0, 0]) color(c_hantel) cylinder(d = kopf, h = kopf_l, $fn = 48);
            translate([-1, y - 1, -kopf + abflachung]) cube([kopf + 2, kopf_l + 2, kopf]);
        }
    translate([kopf / 2, kopf_l, zc]) rotate([-90, 0, 0]) color(c_holz) cylinder(d = griff_d, h = laenge - 2 * kopf_l, $fn = 32);
}

module aufnahme(kopf, laenge, y_hantel) {
    // zwei gepolsterte Auflagen am Griff nahe den Köpfen, Sicherungsbügel an einer Griffschulter
    zg = halter_luft + kopf / 2 - griff_d / 2;       // Oberkante Auflage = Unterseite Griff
    for (y = traverse_y) {
        color(c_stahl) translate([kopf / 2 - 12, y - 6, traverse_b]) cube([24, 12, max(zg - traverse_b - 4, 1)]);
        color(c_leder) translate([kopf / 2 - 14, y - 7, zg - 4]) cube([28, 14, 4]);
    }
    color(c_stahl) translate([kopf / 2 - griff_d / 2 - 4, traverse_y[0] - 3, zg]) difference() {
        cube([griff_d + 8, 6, griff_d + 6]);
        translate([4, -1, -1]) cube([griff_d, 8, griff_d + 3]);
    }
}

module inhalt_zeichnen() {
    for (it = inhalt) {
        typ = it[0]; x = it[1]; y = it[2]; z = it[3];
        b = it[4]; h = it[5]; tf = it[6]; kopf = it[7]; kopf_l = it[8];
        if (typ == "khr") {
            translate([x + 5, 0, z]) aufnahme(kopf, tf, y);
            translate([x + 5, y, z + halter_luft]) hantel_rund(kopf, kopf_l, tf);
        } else {
            translate([x, y, z]) color(c_box) cube([b, tf, h]);
        }
    }
}

// ---------- Zusammenbau ----------

if (zeige_holz) { verkleidung(); rolltuer(); }
rahmen();
fahrwerk();
gelenkkonsolen();
gleitschienen(lehne_achse_x, lehne_dir, lehne_schiene_x0, lehne_schiene_x1, lehne_loecher);
gleitschienen(sitz_achse_x, sitz_dir, sitz_schiene_x0, sitz_schiene_x1, sitz_loecher);
translate([0, 0, 260 * e]) {
    gleitstuetze(lehne_achse_x, lehne_dir, lehne_s, lehne_l_stuetze, lehne_winkel);
    gleitstuetze(sitz_achse_x, sitz_dir, sitz_s, sitz_l_stuetze, sitz_winkel);
}
if (zeige_polster) {
    klappteil(lehne_achse_x, lehne_dir, lehne_laenge, lehne_rippe_l, lehne_s, lehne_winkel);
    klappteil(sitz_achse_x, sitz_dir, sitz_laenge, sitz_rippe_l, sitz_s, sitz_winkel);
    if (geist) {
        for (a = concat([0], lehne_winkel_liste)) if (a != lehne_winkel)
            klappteil(lehne_achse_x, lehne_dir, lehne_laenge, 0, lehne_s, a, 0.18);
        for (a = concat([0], sitz_winkel_liste)) if (a != sitz_winkel)
            klappteil(sitz_achse_x, sitz_dir, sitz_laenge, 0, sitz_s, a, 0.18);
    }
}
if (zeige_inhalt) inhalt_zeichnen();
