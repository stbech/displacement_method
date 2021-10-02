#k_mod-Werte für die unterschiedlichen Nutzungsklassen und Klassen der Lasteinwirkungsdauer

k_mod = {
    '1': {
        'PERM': 0.6,
        'LONG': 0.7,
        'MEDI': 0.8,
        'SHOR': 0.9,
        'MSHO': 1.0,
        'VSHO': 1.1,
    },
    '2': {
        'PERM': 0.6,
        'LONG': 0.7,
        'MEDI': 0.8,
        'SHOR': 0.9,
        'MSHO': 1.0,
        'VSHO': 1.1,
    },
    '3': {
        'PERM': 0.5,
        'LONG': 0.55,
        'MEDI': 0.65,
        'SHOR': 0.7,
        'MSHO': 0.8,
        'VSHO': 0.9,
    },
}



support_Z = [
    (0, 0, 0.75, 1),
    (0, 0, -0.75, 1),
    (0.75, 1, -0.75, 1),
    (1.2, 1.3, -1.2, 1.3),
]

support_XZ = [
    (0    , 0, 0.75, 1),
    (0    , 0, -0.75, 1),
    (1.2  , 1, -1.2, 1),
    (-0.8 , 1, -1.1, 1.3),
    (-0.35, 1, -0.65, 1.3),
    ( 0.1 , 1, -0.2, 1.3),
    ( 0.55, 1,  0.25, 1.3),
    ( 1.00, 1,  0.7, 1.3),
]

support_XY = [
    (0, 1.2, 0, -1.2),
    (-0.3, 1.2, -0.3, -1.2),
    (-0.3, -0.8, -0.6, -1.1),
    (-0.3, -0.35, -0.6, -0.65),
    (-0.3,  0.1, -0.6, -0.2),
    (-0.3, 0.55, -0.6, 0.25),
    (-0.3,  1.0, -0.6, 0.7),
]

support_XYZ = [
    (0, 1.2, 0, -1.2),
    (0, -0.8, -0.3, -1.1),
    (0, -0.35, -0.3, -0.65),
    (0,  0.1, -0.3, -0.2),
    (0, 0.55, -0.3, 0.25),
    (0,  1.0, -0.3, 0.7),
]



gnuplot_vars = {
    'factor_s': [0.2,  '# Größe der Auflager'],
    'factor_l': [0.3,  '# Abstand Text von Systemlinie'],
    'offset'  : [0.2,  '# Abstand Last von Systemlinie'],
    'factor_L': [0.06, '# Skalierung Last'],
    'factor_N': [0.03, '# Skalierung Normalkraft'],
    'factor_V': [0.03, '# Skalierung Querkraft'],
    'factor_M': [0.03, '# Skalierung Moment'],
    'factor_w': [0.03, '# Skalierung Verformung'],
    'factor_t': [0.8,  '# Skalierung Text'],
    'padding' : [1.0,  '# Überstand von Systemlinie zum Rand'],
}