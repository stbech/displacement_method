import parse

#TODO falls Sternchen statt Wert für key -> nimm default
#TODO Exzentrizität für Querschnitte (YM, ZM)?
keywords = {
    'MATQS': {
        'STEU': {
            'KEYS': {
                'NKL':  (int,   1,    False),       # Nutzungsklasse (1, 2, 3)
            },
            'FUNC': parse.change_MATQS_GLOBALS,
        },
        'MAT': {
            'KEYS': {       #TODO STAH, HOLZ definieren und Werte in Datenbank hinterlegen
                'NR':   (int,   None, False),       # Materialnummer
                'E':    (float, 210000, False),     # E-Modul, standardmäßig für Baustahl [MN/m²]
                'GAM':  (float, 78.5, False),       # Wichte, standardmäßig für Baustahl [kN/m³]
                'ALFA': (float, 12  , False),       # Temperaturausdehnungskoeffizient alpha [1/K *E-5]
                'BEZ':  (str,   ""  , False),       # Bezeichnung Material
            },
            'FUNC': parse.create_MAT,
        },
        'QUER': {
            'KEYS': {       
                'NR':   (int,   None, False),       # Querschnittsnummer
                'MNR':  (int,   1,    False),       # Materialnummer
                'A':    (float, 1,    False),       # Querschnittsfläche [m²]
                'IY':   (float, None, False),       # Flächenträgheitsmoment [m^4]; Standard = A^3/12
                'BEZ':  (str,   ""  , False),       # Bezeichnung Querschnitt
            },
            'FUNC': parse.create_CS_QUER,
        },
        'QB': {     #TODO Rotation
            'KEYS': {       
                'NR':   (int,   None, False),       # Querschnittsnummer
                'MNR':  (int,   1,    False),       # Materialnummer
                'H':    (float, 1,    False),       # Querschnittshöhe [m]
                'B':    (float, 1,    False),       # Querschnittsbreite [m]
                'BEZ':  (str,   ""  , False),       # Bezeichnung Querschnitt
            },
            'FUNC': parse.create_CS_QB,
        },
        'QC': {
            'KEYS': {       
                'NR':   (int,   None, False),       # Querschnittsnummer
                'MNR':  (int,   1,    False),       # Materialnummer
                'D':    (float, None, True ),       # Durchmesser [m]
                'T':    (float, 0,    False),       # Wandstärke [m]; falls T=0 -> Vollkreis
                'BEZ':  (str,   ""  , False),       # Bezeichnung Querschnitt
            },
            'FUNC': parse.create_CS_QC,
        },
        'PROF': {   #TODO nicht funktionsfähig -> Profilliste erstellen #TODO Rotation
            'KEYS': {       
                'NR':   (int,   None, False),       # Querschnittsnummer
                'MNR':  (int,   1,    False),       # Materialnummer
                'TYP':  (float, None, True ),       # Profiltyp
                'Z1':   (float, None, True ),       # Bezeichner Profil
                'Z2':   (float, None, False),       # Bezeichner Profil
                'BEZ':  (str,   ""  , False),       # Bezeichnung Querschnitt
            },
            'FUNC': parse.create_CS_PROF,
        },
        #'QNR': {},
        #'QW': {},
    },
    'SYSTEM': {
        'STEU': {
            'KEYS': {#TODO Eigengewichtsrichtung
                'HMIN': (float, -10,  False),       # globaler Stabteiler: positiv -> max. Abstand Zwischenknoten [m], negativ + int -> Anzahl Unterteilungen
            },
            'FUNC': parse.change_SYSTEM_GLOBALS,
        },
        'SPT': {
            'KEYS': {
                'NR':   (int,   None, False),       # Knotennummer
                'X':    (float, 0   , False),       # x-Koordinate [m]
                'Z':    (float, 0   , False),       # z-Koordinate [m]
                'FIX':  (str,   ""  , False),       # Auflagerbedingungen (PX, PZ, PP, MY, FF)
                'NX':   (float, 1   , False),       # Ausrichtung lokales Koordinatensystem
                'NZ':   (float, 0   , False),   
                'ALPH': (float, 0   , False),       # entweder über Drehwinkel oder Vorgabe Richtung [°]
                'BEZ':  (str,   ""  , False),       # Bezeichnung Knoten
            },
            'FUNC': parse.create_SPT,
        },  
        'SPTS': {  
            'KEYS': {
                'CP':   (float, 0   , False),       # Federsteifigkeit in axiale Richtung oder in lokal x [kN/m]
                'CQ':   (float, 0   , False),       # Federsteifigkeit in Querrichtung oder in lokal z [kN/m]
                'CM':   (float, 0   , False),       # Rotationssteifigkeit [kNm/rad]
            },
            'FUNC': parse.add_SPTS,
        },  
        'SLN': {  
            'KEYS': {
                'NR':   (int,   None, False),       # Stabnummer
                'NPA':  (int,   None, True ),       # Knoten am Stabanfang
                'NPE':  (int,   None, True ),       # Knoten am Stabende
                'SDIV': (float, None, False),       # lokaler Stabteiler: positiv -> max. Abstand Zwischenknoten [m], negativ + int -> Anzahl Unterteilungen; überschreibt STEU HMIN
                'QNR':  (int,   1,    False),       # Querschnittsnummer
                'FIXA': (str,   ""  , False),       # Gelenkbedingung am Stabanfang (N, V oder VZ, PP, M oder MY oder MM)
                'FIXE': (str,   ""  , False),       # Gelenkbedingung am Stabende (N, V oder VZ, PP, M oder MY oder MM)
                'BEZ':  (str,   ""  , False),       # Bezeichnung Stab
            },
            'FUNC': parse.create_SLN,  
        },
    },
    'LOAD': {
        'ACT': {
            'KEYS': {
                'TYP':  (str,   None, False),       # Bezeichnung
                'GAMU': (float, None, False),       # Teilsicherheitsbeiwert ungünstig
                'GAMF': (float, None, False),       # Teilsicherheitsbeiwert günstig
                'PSI0': (float, None, False),       # Kombinationsbeiwert selten
                'PSI1': (float, None, False),       # Kombinationsbeiwert häufig
                'PSI2': (float, None, False),       # Kombinationsbeiwert quasi-ständig
                #'KMOD': (float, 1.0,  False),       # Modifikationsbeiwert (für den Holzbau)
                'KLED': (str,   None, False),       # Klasse der Lasteinwirkungsdauer (PERM, LONG, MEDI, SHOR, MSHO, VSHO)
                'PART': (str,   'G',  False),       # Art der Einwirkung (G oder Q)
                'SUP':  (str,   None, False),       # Standardüberlagerung siehe sofiload S. 22
                'BEZ':  (str,   ""  , False),       # Bezeichnung Einwirkung
            },
            'FUNC': parse.create_ACT,
        },
        'LF': {
            'KEYS': {
                'NR':   (int,   None, False),       # Lastfallnummer
                'TYP':  (str,   None, True),        # Typ des Lastfalls (definiert in ACT)
                'FAKT': (float, 1.0,  False),       # Faktor Lastfall (wirkt nicht auf FAKG)
                'FAKG': (float, 0.0,  False),       # Faktor Eigengewicht (keine anderen Lasten mehr ansetzbar) #TODO was ist mit EGZ?
                'BEZ':  (str,   ""  , False),       # Bezeichnung Lastfall
            },
            'FUNC': parse.create_LF,
        },
        'KNOT': {#TODO ALPH Literal?
            'KEYS': {
                'NR':   (int,   None, True),        # Knotennummer
                'TYP':  (str,   'PG', False),       # Lastart und Richtung (PG, PX(X), PZ(Z), MY(Y), P(P), V(V), WX(X), WZ(Z), DY(Y))
                'P1':   (float, 0,    False),       # Lastwert 1
                'P2':   (float, 0,    False),       # Lastwert 2
                'P3':   (float, 0,    False),       # Lastwert 3
                'EXX':  (float, 0,    False),       # Exzentrizität in x-Richtung [m] (lokal falls PZ/PX, global falls PZZ/PXX)
                'EZZ':  (float, 0,    False),       # Exzentrizität in z-Richtung [m]
            },
            'FUNC': parse.add_KNOT,
        },
        'STAB': {#TODO Rechne DT und DTZ intern in EX, KY um
            'KEYS': {
                'NR':   (int,   '1' , False),       # Stabnummer
                'TYP':  (str,   'PG', False),       # Lastart und Richtung (PG, PX(X), PZ(Z), EX, KY, DT, DTZ)
                'PA':   (float, 0,    False),       # Lastwert Anfang
                'PE':   (float, None, False),       # Lastwert Ende (default wie Anfang)
                'A':    (float, 0,    False),       # Abstand des Lastanfangs vom Stabanfang/-ende [m]
                'L':    (float, None, False),       # Länge der Last [m]
                'MESS': (str,   'S',  False),       # Bezugssystem für A, L (S, XX, ZZ) (Minus voranstellen, falls auf Stabende bezogen)
            },
            'FUNC': parse.add_STAB,
        },
        'STEL': {
            'KEYS': {
                'NR':   (int,   '1' , False),       # Stabnummer
                'TYP':  (str,   'PG', False),       # Lastart und Richtung (PG, PX(X), PZ(Z), MY(Y))
                'P':    (float, 0,    False),       # Lastwert Anfang
                'A':    (float, 0,    False),       # Abstand der Last vom Stabanfang/-ende [m]
                'MESS': (str,   'S',  False),       # Bezugssystem für A, L (S, XX, ZZ) (- voranstellen, falls auf Stabende bezogen)
            },
            'FUNC': parse.add_STEL,
        },
        'COPY': {
            'KEYS': {
                'NR':   (int,   None, True ),       # Stabnummer
                'FAKT': (float, 1.0,  False),       # Faktor Lastfall
            },
            'FUNC': parse.copy_LC,
        },
    }, 
    'CALC': {
        'LF': {
            'KEYS': {
                'NR':   (str,   None, True ),       # zu berechnende Lastfälle
            },
            'FUNC': parse.add_LC_calc,
        },
    },
    'COMB': {# Lastfälle DESI, RARE, FREQ, PERM; #TODO ACT benötigt?
        'STEU': {
            'KEYS': {
                'KLED': (str,  'NEIN', False),     # Steuert Überlagerung getrennt nach k_mod-Werten (Klassen der Lasteinwirkungsdauer)
            },
            'FUNC': parse.change_COMB_GLOBALS,
        },
        'KOMB': {
            'KEYS': {
                'NR':   (int,   None, False),       # Nummer der Kombination
                'EXTR': (str,   'STAN', False),     # Überlagerungsart (STAN, DESI, PERM, RARE, FREQ)
                #'BASE': (int,   None, False),       # Basislastfallnummer (Vielfaches von 100)
            },
            'FUNC': parse.create_KOMB,
        },
        'ACT': {
            'KEYS': {
                'TYP':  (str,   None, True ),       # Bezeichnung
            },
            'FUNC': parse.change_ACT,
        },
        'LF': {
            'KEYS': {
                'NR':   (int,   None, True ),       # Nummer der Lastfalls
                'TYPE': (str,   None, True ),       # Überlagerungsart (G (PERM), PERC, Q (COND), AG_ (ALEX=AG1), A_ (EXCL))
            },
            'FUNC': parse.add_LC_comb,
        },
        'SUPP': {#KNOT: PX, PZ, MY, UX, UZ, URY, global und lokal? #STAB N, VZ, MY, UX, UZ, URY? #FEDE P, PT, M
            'KEYS': {
                'KOMB': (int,   '1',  False),       # Nummer der Kombination
                'EXTR': (str,   'MAMI', False),     # Extremalbedingung (MAX, MIN, MAMI)
                'ETYP': (str,   None, True ),       # Elementtyp (KNOT, STAB, FEDE?)
                'ZUST': (str,   None, True ),       # zu überlagernde Zustandsgröße abhängig von ETYP
                #'BEZ':  (str,   ""  , False),       # Bezeichnung Überlagerungslastfall
            },
            'FUNC': parse.add_SUPP,
        },
    }
}
