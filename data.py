"""
data.py - Fixtures, equipos y constantes del Prode Mundial 2026
"""

# ============================================================
# GRUPOS Y EQUIPOS
# ============================================================
GROUPS = {
    "A": ["MEXICO", "SUDAFRICA", "COREA DEL SUR", "REP. CHECA"],
    "B": ["CANADA", "BOSNIA", "QATAR", "SUIZA"],
    "C": ["BRASIL", "MARRUECOS", "HAITI", "ESCOCIA"],
    "D": ["ESTADOS UNIDOS", "PARAGUAY", "AUSTRALIA", "TURQUIA"],
    "E": ["ALEMANIA", "CURAZAO", "COSTA DE MARFIL", "ECUADOR"],
    "F": ["PAISES BAJOS", "JAPON", "SUECIA", "TUNEZ"],
    "G": ["BELGICA", "EGIPTO", "IRAN", "NUEVA ZELANDA"],
    "H": ["ESPANA", "CABO VERDE", "ARABIA SAUDITA", "URUGUAY"],
    "I": ["FRANCIA", "SENEGAL", "IRAK", "NORUEGA"],
    "J": ["ARGENTINA", "ARGELIA", "AUSTRIA", "JORDANIA"],
    "K": ["PORTUGAL", "RD CONGO", "UZBEKISTAN", "COLOMBIA"],
    "L": ["INGLATERRA", "CROACIA", "GHANA", "PANAMA"],
}

# ============================================================
# PARTIDOS DE FASE DE GRUPOS (72 partidos)
# Formato: (grupo, nro_partido, equipo_local, equipo_visitante)
# ============================================================
GROUP_MATCHES = [
    # GRUPO A
    ("A", 1, "MEXICO", "SUDAFRICA"),
    ("A", 2, "COREA DEL SUR", "REP. CHECA"),
    ("A", 3, "MEXICO", "COREA DEL SUR"),
    ("A", 4, "REP. CHECA", "SUDAFRICA"),
    ("A", 5, "REP. CHECA", "MEXICO"),
    ("A", 6, "SUDAFRICA", "COREA DEL SUR"),
    # GRUPO B
    ("B", 1, "CANADA", "BOSNIA"),
    ("B", 2, "QATAR", "SUIZA"),
    ("B", 3, "CANADA", "QATAR"),
    ("B", 4, "SUIZA", "BOSNIA"),
    ("B", 5, "SUIZA", "CANADA"),
    ("B", 6, "BOSNIA", "QATAR"),
    # GRUPO C
    ("C", 1, "BRASIL", "MARRUECOS"),
    ("C", 2, "HAITI", "ESCOCIA"),
    ("C", 3, "BRASIL", "HAITI"),
    ("C", 4, "ESCOCIA", "MARRUECOS"),
    ("C", 5, "ESCOCIA", "BRASIL"),
    ("C", 6, "MARRUECOS", "HAITI"),
    # GRUPO D
    ("D", 1, "ESTADOS UNIDOS", "PARAGUAY"),
    ("D", 2, "AUSTRALIA", "TURQUIA"),
    ("D", 3, "ESTADOS UNIDOS", "AUSTRALIA"),
    ("D", 4, "TURQUIA", "PARAGUAY"),
    ("D", 5, "TURQUIA", "ESTADOS UNIDOS"),
    ("D", 6, "PARAGUAY", "AUSTRALIA"),
    # GRUPO E
    ("E", 1, "ALEMANIA", "CURAZAO"),
    ("E", 2, "COSTA DE MARFIL", "ECUADOR"),
    ("E", 3, "ALEMANIA", "COSTA DE MARFIL"),
    ("E", 4, "ECUADOR", "CURAZAO"),
    ("E", 5, "ECUADOR", "ALEMANIA"),
    ("E", 6, "CURAZAO", "COSTA DE MARFIL"),
    # GRUPO F
    ("F", 1, "PAISES BAJOS", "JAPON"),
    ("F", 2, "SUECIA", "TUNEZ"),
    ("F", 3, "PAISES BAJOS", "SUECIA"),
    ("F", 4, "TUNEZ", "JAPON"),
    ("F", 5, "TUNEZ", "PAISES BAJOS"),
    ("F", 6, "JAPON", "SUECIA"),
    # GRUPO G
    ("G", 1, "BELGICA", "EGIPTO"),
    ("G", 2, "IRAN", "NUEVA ZELANDA"),
    ("G", 3, "BELGICA", "IRAN"),
    ("G", 4, "NUEVA ZELANDA", "EGIPTO"),
    ("G", 5, "NUEVA ZELANDA", "BELGICA"),
    ("G", 6, "EGIPTO", "IRAN"),
    # GRUPO H
    ("H", 1, "ESPANA", "CABO VERDE"),
    ("H", 2, "ARABIA SAUDITA", "URUGUAY"),
    ("H", 3, "ESPANA", "ARABIA SAUDITA"),
    ("H", 4, "URUGUAY", "CABO VERDE"),
    ("H", 5, "URUGUAY", "ESPANA"),
    ("H", 6, "CABO VERDE", "ARABIA SAUDITA"),
    # GRUPO I
    ("I", 1, "FRANCIA", "SENEGAL"),
    ("I", 2, "IRAK", "NORUEGA"),
    ("I", 3, "FRANCIA", "IRAK"),
    ("I", 4, "NORUEGA", "SENEGAL"),
    ("I", 5, "NORUEGA", "FRANCIA"),
    ("I", 6, "SENEGAL", "IRAK"),
    # GRUPO J
    ("J", 1, "ARGENTINA", "ARGELIA"),
    ("J", 2, "AUSTRIA", "JORDANIA"),
    ("J", 3, "ARGENTINA", "AUSTRIA"),
    ("J", 4, "JORDANIA", "ARGELIA"),
    ("J", 5, "JORDANIA", "ARGENTINA"),
    ("J", 6, "ARGELIA", "AUSTRIA"),
    # GRUPO K
    ("K", 1, "PORTUGAL", "RD CONGO"),
    ("K", 2, "UZBEKISTAN", "COLOMBIA"),
    ("K", 3, "PORTUGAL", "UZBEKISTAN"),
    ("K", 4, "COLOMBIA", "RD CONGO"),
    ("K", 5, "COLOMBIA", "PORTUGAL"),
    ("K", 6, "RD CONGO", "UZBEKISTAN"),
    # GRUPO L
    ("L", 1, "INGLATERRA", "CROACIA"),
    ("L", 2, "GHANA", "PANAMA"),
    ("L", 3, "INGLATERRA", "GHANA"),
    ("L", 4, "PANAMA", "CROACIA"),
    ("L", 5, "PANAMA", "INGLATERRA"),
    ("L", 6, "CROACIA", "GHANA"),
]

# ============================================================
# BRACKET DE PLAYOFFS (16avos de final)
# Formato: (posicion_bracket, equipo_local_tipo, equipo_visitante_tipo)
# Los 3ros se resuelven dinámicamente según clasificación
# ============================================================
PLAYOFF_BRACKET_16 = [
    # Lado izquierdo
    ("16avos_L1", "1H", "2J"),      # ESPANA vs AUSTRIA
    ("16avos_L2", "1I", "3CDFGH"),   # FRANCIA vs 3ro(CDFGH)
    ("16avos_L3", "1C", "2F"),       # MARRUECOS vs SUECIA
    ("16avos_L4", "2E", "2I"),       # ECUADOR vs NORUEGA
    ("16avos_L5", "1A", "3CEFHI"),   # REP. CHECA vs 3ro(CEFHI)
    ("16avos_L6", "2D", "2G"),       # PARAGUAY vs IRAN
    ("16avos_L7", "1D", "3BEFIJ"),   # AUSTRALIA vs 3ro(BEFIJ)
    ("16avos_L8", "1K", "3DEIJL"),   # PORTUGAL vs 3ro(DEIJL)
    # Lado derecho
    ("16avos_R1", "1G", "3AEHIJ"),   # BELGICA vs 3ro(AEHIJ)
    ("16avos_R2", "1B", "3EFGIJ"),   # SUIZA vs 3ro(EFGIJ)
    ("16avos_R3", "1F", "2C"),       # PAISES BAJOS vs BRASIL
    ("16avos_R4", "1L", "3EHIJK"),   # INGLATERRA vs 3ro(EHIJK)
    ("16avos_R5", "2K", "2L"),       # COLOMBIA vs GHANA
    ("16avos_R6", "1E", "3ABCDF"),   # ALEMANIA vs 3ro(ABCDF)
    ("16avos_R7", "2A", "2B"),       # COREA DEL SUR vs BOSNIA
    ("16avos_R8", "1J", "2H"),       # ARGENTINA vs ARABIA SAUDITA
]

PLAYOFF_ROUNDS = ["16avos", "octavos", "cuartos", "semifinal", "final", "tercer_puesto"]

# ============================================================
# JUGADORES REGISTRADOS (del spreadsheet original)
# ============================================================
REGISTERED_PLAYERS = [
    "Nicolas Salazar",
    "Roman Sabbatiello",
    "Guido Cardero",
    "Mariano Ivaldi",
    "Diego Kotler",
    "Sergio Kotler",
    "Noelia Ritacco",
    "Pablo Manente",
    "Santiago Vazquez",
    "Matias Miguez",
    "Maximiliano Paz",
    "Ariel Tubello",
    "Lucas Zagarchuk",
    "Alberto Ostolaza",
    "Juan Manuel Arrebola",
    "Steven Mc Intyre",
    "Alejandro Barrera",
    "Nicolas Etchelecu",
    "Ivan Dankiewicz",
    "Damian Carubino",
    "Joaquin Corral",
    "Francesca Giordano",
]

# ============================================================
# INSTANCIAS DE COBRO (ETAPAS DE PREMIOS)
# ============================================================
PRIZE_STAGES = {
    1: {"name": "Etapa 1", "groups": ["A", "B", "C", "D"]},
    2: {"name": "Etapa 2", "groups": ["E", "F", "G", "H"]},
    3: {"name": "Etapa 3", "groups": ["I", "J", "K", "L"]},
    4: {"name": "Etapa 4", "rounds": ["16avos"]},
    5: {"name": "Etapa 5", "rounds": ["octavos"]},
    6: {"name": "Etapa 6", "rounds": ["cuartos", "semifinal", "final", "tercer_puesto"]},
}

# Lista de todos los equipos participantes (48)
ALL_TEAMS = sorted(set(team for teams in GROUPS.values() for team in teams))

# ============================================================
# FECHA DE INICIO DEL MUNDIAL
# Partido inaugural: 11 junio 2026 · 21:00 hs Argentina (UTC-3)
# En UTC eso es el 12 de junio a las 00:00
# ============================================================
WORLD_CUP_START_UTC = "2026-06-12T00:00:00Z"
WORLD_CUP_START_LABEL = "11 de junio 2026 · 21:00 hs (ARG) · Estadio Azteca, Ciudad de México"

# ============================================================
# FASES DEL TORNEO (fechas en horario Argentina / UTC-3)
# ============================================================
TOURNAMENT_PHASES = [
    {
        "phase": "Fase de Grupos · Jornada 1",
        "start": "11 jun",
        "end": "17 jun",
        "color": "#2980B9",
        "emoji": "⚽",
    },
    {
        "phase": "Fase de Grupos · Jornada 2",
        "start": "17 jun",
        "end": "23 jun",
        "color": "#2980B9",
        "emoji": "⚽",
    },
    {
        "phase": "Fase de Grupos · Jornada 3",
        "start": "23 jun",
        "end": "27 jun",
        "color": "#2980B9",
        "emoji": "⚽",
    },
    {
        "phase": "Dieciseisavos de Final",
        "start": "29 jun",
        "end": "3 jul",
        "color": "#8E44AD",
        "emoji": "⚔️",
    },
    {
        "phase": "Octavos de Final",
        "start": "6 jul",
        "end": "9 jul",
        "color": "#8E44AD",
        "emoji": "⚔️",
    },
    {
        "phase": "Cuartos de Final",
        "start": "12 jul",
        "end": "13 jul",
        "color": "#E67E22",
        "emoji": "🔥",
    },
    {
        "phase": "Semifinales",
        "start": "16 jul",
        "end": "17 jul",
        "color": "#E67E22",
        "emoji": "🔥",
    },
    {
        "phase": "Tercer Puesto",
        "start": "19 jul",
        "end": "19 jul",
        "color": "#95A5A6",
        "emoji": "🥉",
    },
    {
        "phase": "GRAN FINAL",
        "start": "19 jul",
        "end": "19 jul",
        "color": "#F1C40F",
        "emoji": "🏆",
    },
]

# ============================================================
# SEDES DEL MUNDIAL 2026 (16 estadios)
# ============================================================
VENUES = [
    # México
    {
        "name": "Estadio Azteca", "city": "Ciudad de México", "country": "México",
        "capacity": 87_000, "flag": "🇲🇽",
        "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Azteca_Stadium.jpg/640px-Azteca_Stadium.jpg",
    },
    {
        "name": "Estadio BBVA", "city": "Monterrey", "country": "México",
        "capacity": 53_500, "flag": "🇲🇽",
        "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Estadio_BBVA_Bancomer.jpg/640px-Estadio_BBVA_Bancomer.jpg",
    },
    {
        "name": "Estadio Akron", "city": "Guadalajara", "country": "México",
        "capacity": 46_400, "flag": "🇲🇽",
        "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/16/Estadio_Akron.jpg/640px-Estadio_Akron.jpg",
    },
    # Canadá
    {
        "name": "BC Place", "city": "Vancouver", "country": "Canadá",
        "capacity": 54_500, "flag": "🇨🇦",
        "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/BC_Place_2014.jpg/640px-BC_Place_2014.jpg",
    },
    {
        "name": "BMO Field", "city": "Toronto", "country": "Canadá",
        "capacity": 45_000, "flag": "🇨🇦",
        "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/BMO_Field_2016.jpg/640px-BMO_Field_2016.jpg",
    },
    {
        "name": "Stade Olympique", "city": "Montreal", "country": "Canadá",
        "capacity": 61_000, "flag": "🇨🇦",
        "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Montreal_Olympic_Stadium.jpg/640px-Montreal_Olympic_Stadium.jpg",
    },
    # Estados Unidos
    {
        "name": "MetLife Stadium", "city": "Nueva York / NJ", "country": "USA",
        "capacity": 82_500, "flag": "🇺🇸",
        "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/MetLife_Stadium_Giants_Jets.jpg/640px-MetLife_Stadium_Giants_Jets.jpg",
    },
    {
        "name": "AT&T Stadium", "city": "Dallas", "country": "USA",
        "capacity": 80_000, "flag": "🇺🇸",
        "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/Cowboys_Stadium_exterior.jpg/640px-Cowboys_Stadium_exterior.jpg",
    },
    {
        "name": "SoFi Stadium", "city": "Los Ángeles", "country": "USA",
        "capacity": 70_240, "flag": "🇺🇸",
        "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/SoFi_Stadium_2020.jpg/640px-SoFi_Stadium_2020.jpg",
    },
    {
        "name": "Rose Bowl", "city": "Pasadena", "country": "USA",
        "capacity": 88_565, "flag": "🇺🇸",
        "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d9/Rose_Bowl_Stadium_2016.jpg/640px-Rose_Bowl_Stadium_2016.jpg",
    },
    {
        "name": "Levi's Stadium", "city": "San Francisco", "country": "USA",
        "capacity": 68_500, "flag": "🇺🇸",
        "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Levi%27s_Stadium.jpg/640px-Levi%27s_Stadium.jpg",
    },
    {
        "name": "Arrowhead Stadium", "city": "Kansas City", "country": "USA",
        "capacity": 76_416, "flag": "🇺🇸",
        "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/Arrowhead_Stadium_2013.jpg/640px-Arrowhead_Stadium_2013.jpg",
    },
    {
        "name": "Lincoln Financial Field", "city": "Filadelfia", "country": "USA",
        "capacity": 69_176, "flag": "🇺🇸",
        "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/Lincoln_Financial_Field.jpg/640px-Lincoln_Financial_Field.jpg",
    },
    {
        "name": "Gillette Stadium", "city": "Boston", "country": "USA",
        "capacity": 65_878, "flag": "🇺🇸",
        "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Gillette_Stadium_2012.jpg/640px-Gillette_Stadium_2012.jpg",
    },
    {
        "name": "NRG Stadium", "city": "Houston", "country": "USA",
        "capacity": 72_220, "flag": "🇺🇸",
        "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a4/NRG_Stadium_2017.jpg/640px-NRG_Stadium_2017.jpg",
    },
    {
        "name": "Hard Rock Stadium", "city": "Miami", "country": "USA",
        "capacity": 65_326, "flag": "🇺🇸",
        "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Hard_Rock_Stadium_2016.jpg/640px-Hard_Rock_Stadium_2016.jpg",
    },
]

# ============================================================
# HORARIOS APROXIMADOS DE LOS PARTIDOS (hora Argentina UTC-3)
# Basado en el fixture oficial FIFA 2026.
# Formato: (grupo, nro_partido): (fecha, hora_arg, estadio, ciudad)
# ============================================================
MATCH_SCHEDULE = {
    # ── GRUPO A  (Mexico / Sudafrica / Corea del Sur / Rep. Checa)
    ("A", 1): ("11 jun", "22:00", "Estadio Azteca",       "Ciudad de México"),
    ("A", 2): ("12 jun", "19:00", "Estadio Azteca",       "Ciudad de México"),
    ("A", 3): ("16 jun", "22:00", "Estadio Azteca",       "Ciudad de México"),
    ("A", 4): ("17 jun", "19:00", "Estadio Azteca",       "Ciudad de México"),
    ("A", 5): ("23 jun", "22:00", "Estadio Azteca",       "Ciudad de México"),
    ("A", 6): ("23 jun", "22:00", "Estadio Azteca",       "Ciudad de México"),

    # ── GRUPO B  (Canada / Bosnia / Qatar / Suiza)
    ("B", 1): ("12 jun", "22:00", "BC Place",             "Vancouver"),
    ("B", 2): ("13 jun", "19:00", "Stade Olympique",      "Montreal"),
    ("B", 3): ("17 jun", "22:00", "BC Place",             "Vancouver"),
    ("B", 4): ("18 jun", "19:00", "BMO Field",            "Toronto"),
    ("B", 5): ("24 jun", "22:00", "BC Place",             "Vancouver"),
    ("B", 6): ("24 jun", "22:00", "Stade Olympique",      "Montreal"),

    # ── GRUPO C  (Brasil / Marruecos / Haiti / Escocia)
    ("C", 1): ("13 jun", "22:00", "SoFi Stadium",         "Los Ángeles"),
    ("C", 2): ("14 jun", "19:00", "Rose Bowl",            "Pasadena"),
    ("C", 3): ("18 jun", "22:00", "SoFi Stadium",         "Los Ángeles"),
    ("C", 4): ("19 jun", "19:00", "Rose Bowl",            "Pasadena"),
    ("C", 5): ("25 jun", "22:00", "SoFi Stadium",         "Los Ángeles"),
    ("C", 6): ("25 jun", "22:00", "Rose Bowl",            "Pasadena"),

    # ── GRUPO D  (Estados Unidos / Paraguay / Australia / Turquia)
    ("D", 1): ("12 jun", "21:00", "MetLife Stadium",      "Nueva York"),
    ("D", 2): ("13 jun", "18:00", "Gillette Stadium",     "Boston"),
    ("D", 3): ("17 jun", "21:00", "MetLife Stadium",      "Nueva York"),
    ("D", 4): ("18 jun", "18:00", "Lincoln Financial",    "Filadelfia"),
    ("D", 5): ("23 jun", "21:00", "MetLife Stadium",      "Nueva York"),
    ("D", 6): ("23 jun", "21:00", "Gillette Stadium",     "Boston"),

    # ── GRUPO E  (Alemania / Curazao / Costa de Marfil / Ecuador)
    ("E", 1): ("14 jun", "22:00", "AT&T Stadium",         "Dallas"),
    ("E", 2): ("15 jun", "19:00", "Arrowhead Stadium",    "Kansas City"),
    ("E", 3): ("19 jun", "22:00", "AT&T Stadium",         "Dallas"),
    ("E", 4): ("20 jun", "19:00", "Arrowhead Stadium",    "Kansas City"),
    ("E", 5): ("26 jun", "22:00", "AT&T Stadium",         "Dallas"),
    ("E", 6): ("26 jun", "22:00", "Arrowhead Stadium",    "Kansas City"),

    # ── GRUPO F  (Paises Bajos / Japon / Suecia / Tunez)
    ("F", 1): ("15 jun", "22:00", "Levi's Stadium",       "San Francisco"),
    ("F", 2): ("16 jun", "19:00", "Rose Bowl",            "Pasadena"),
    ("F", 3): ("20 jun", "22:00", "Levi's Stadium",       "San Francisco"),
    ("F", 4): ("21 jun", "19:00", "Rose Bowl",            "Pasadena"),
    ("F", 5): ("27 jun", "22:00", "Levi's Stadium",       "San Francisco"),
    ("F", 6): ("27 jun", "22:00", "Rose Bowl",            "Pasadena"),

    # ── GRUPO G  (Belgica / Egipto / Iran / Nueva Zelanda)
    ("G", 1): ("14 jun", "21:00", "NRG Stadium",          "Houston"),
    ("G", 2): ("15 jun", "18:00", "Hard Rock Stadium",    "Miami"),
    ("G", 3): ("19 jun", "21:00", "NRG Stadium",          "Houston"),
    ("G", 4): ("20 jun", "18:00", "Hard Rock Stadium",    "Miami"),
    ("G", 5): ("25 jun", "21:00", "NRG Stadium",          "Houston"),
    ("G", 6): ("25 jun", "21:00", "Hard Rock Stadium",    "Miami"),

    # ── GRUPO H  (España / Cabo Verde / Arabia Saudita / Uruguay)
    ("H", 1): ("13 jun", "21:00", "Hard Rock Stadium",    "Miami"),
    ("H", 2): ("14 jun", "18:00", "NRG Stadium",          "Houston"),
    ("H", 3): ("18 jun", "21:00", "Hard Rock Stadium",    "Miami"),
    ("H", 4): ("19 jun", "18:00", "NRG Stadium",          "Houston"),
    ("H", 5): ("24 jun", "21:00", "Hard Rock Stadium",    "Miami"),
    ("H", 6): ("24 jun", "21:00", "NRG Stadium",          "Houston"),

    # ── GRUPO I  (Francia / Senegal / Irak / Noruega)
    ("I", 1): ("15 jun", "21:00", "MetLife Stadium",      "Nueva York"),
    ("I", 2): ("16 jun", "18:00", "Lincoln Financial",    "Filadelfia"),
    ("I", 3): ("20 jun", "21:00", "MetLife Stadium",      "Nueva York"),
    ("I", 4): ("21 jun", "18:00", "Gillette Stadium",     "Boston"),
    ("I", 5): ("26 jun", "21:00", "MetLife Stadium",      "Nueva York"),
    ("I", 6): ("26 jun", "21:00", "Lincoln Financial",    "Filadelfia"),

    # ── GRUPO J  (Argentina / Argelia / Austria / Jordania)
    ("J", 1): ("11 jun", "21:00", "AT&T Stadium",         "Dallas"),
    ("J", 2): ("12 jun", "18:00", "Arrowhead Stadium",    "Kansas City"),
    ("J", 3): ("16 jun", "21:00", "AT&T Stadium",         "Dallas"),
    ("J", 4): ("17 jun", "18:00", "Arrowhead Stadium",    "Kansas City"),
    ("J", 5): ("22 jun", "21:00", "AT&T Stadium",         "Dallas"),
    ("J", 6): ("22 jun", "21:00", "Arrowhead Stadium",    "Kansas City"),

    # ── GRUPO K  (Portugal / RD Congo / Uzbekistan / Colombia)
    ("K", 1): ("16 jun", "21:00", "Levi's Stadium",       "San Francisco"),
    ("K", 2): ("17 jun", "18:00", "SoFi Stadium",         "Los Ángeles"),
    ("K", 3): ("21 jun", "21:00", "Levi's Stadium",       "San Francisco"),
    ("K", 4): ("22 jun", "18:00", "SoFi Stadium",         "Los Ángeles"),
    ("K", 5): ("27 jun", "21:00", "Levi's Stadium",       "San Francisco"),
    ("K", 6): ("27 jun", "21:00", "SoFi Stadium",         "Los Ángeles"),

    # ── GRUPO L  (Inglaterra / Croacia / Ghana / Panama)
    ("L", 1): ("13 jun", "22:00", "Estadio BBVA",         "Monterrey"),
    ("L", 2): ("14 jun", "19:00", "Estadio Akron",        "Guadalajara"),
    ("L", 3): ("18 jun", "22:00", "Estadio BBVA",         "Monterrey"),
    ("L", 4): ("19 jun", "19:00", "Estadio Akron",        "Guadalajara"),
    ("L", 5): ("24 jun", "22:00", "Estadio BBVA",         "Monterrey"),
    ("L", 6): ("24 jun", "22:00", "Estadio Akron",        "Guadalajara"),
}
