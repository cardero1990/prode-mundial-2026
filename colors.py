"""
colors.py - Paleta de colores oficiales de los 48 equipos del Mundial 2026
Basados en camiseta principal o color mas representativo del pais.
"""

# primary  = color de fondo del chip
# text     = color del texto sobre ese fondo (blanco o casi negro para contraste)
TEAM_COLORS = {
    # ── GRUPO A ──────────────────────────────────────────────
    "MEXICO":          {"primary": "#006847", "text": "#FFFFFF"},
    "SUDAFRICA":       {"primary": "#007A4D", "text": "#FFB81C"},
    "COREA DEL SUR":   {"primary": "#C60C30", "text": "#FFFFFF"},
    "REP. CHECA":      {"primary": "#D7141A", "text": "#FFFFFF"},

    # ── GRUPO B ──────────────────────────────────────────────
    "CANADA":          {"primary": "#D80621", "text": "#FFFFFF"},
    "BOSNIA":          {"primary": "#003DA5", "text": "#FFCC00"},
    "QATAR":           {"primary": "#8D1B3D", "text": "#FFFFFF"},
    "SUIZA":           {"primary": "#CC0000", "text": "#FFFFFF"},

    # ── GRUPO C ──────────────────────────────────────────────
    "BRASIL":          {"primary": "#009C3B", "text": "#FFDF00"},
    "MARRUECOS":       {"primary": "#C1272D", "text": "#FFFFFF"},
    "HAITI":           {"primary": "#00209F", "text": "#FFFFFF"},
    "ESCOCIA":         {"primary": "#003087", "text": "#FFFFFF"},

    # ── GRUPO D ──────────────────────────────────────────────
    "ESTADOS UNIDOS":  {"primary": "#002868", "text": "#FFFFFF"},
    "PARAGUAY":        {"primary": "#D52B1E", "text": "#FFFFFF"},
    "AUSTRALIA":       {"primary": "#FFCD00", "text": "#1A1A1A"},
    "TURQUIA":         {"primary": "#E30A17", "text": "#FFFFFF"},

    # ── GRUPO E ──────────────────────────────────────────────
    "ALEMANIA":        {"primary": "#3D3D3D", "text": "#FFFFFF"},
    "CURAZAO":         {"primary": "#003DA5", "text": "#F9A12E"},
    "COSTA DE MARFIL": {"primary": "#F77F00", "text": "#FFFFFF"},
    "ECUADOR":         {"primary": "#FFD100", "text": "#1A1A1A"},

    # ── GRUPO F ──────────────────────────────────────────────
    "PAISES BAJOS":    {"primary": "#FF6600", "text": "#FFFFFF"},
    "JAPON":           {"primary": "#BC002D", "text": "#FFFFFF"},
    "SUECIA":          {"primary": "#006AA7", "text": "#FECC02"},
    "TUNEZ":           {"primary": "#E70013", "text": "#FFFFFF"},

    # ── GRUPO G ──────────────────────────────────────────────
    "BELGICA":         {"primary": "#ED2939", "text": "#FFFFFF"},
    "EGIPTO":          {"primary": "#CE1126", "text": "#FFFFFF"},
    "IRAN":            {"primary": "#239F40", "text": "#FFFFFF"},
    "NUEVA ZELANDA":   {"primary": "#2C2C2C", "text": "#FFFFFF"},

    # ── GRUPO H ──────────────────────────────────────────────
    "ESPANA":          {"primary": "#C60B1E", "text": "#FFC400"},
    "CABO VERDE":      {"primary": "#003893", "text": "#FFFFFF"},
    "ARABIA SAUDITA":  {"primary": "#006C35", "text": "#FFFFFF"},
    "URUGUAY":         {"primary": "#5EB6E4", "text": "#FFFFFF"},

    # ── GRUPO I ──────────────────────────────────────────────
    "FRANCIA":         {"primary": "#002395", "text": "#FFFFFF"},
    "SENEGAL":         {"primary": "#00853F", "text": "#FDEF42"},
    "IRAK":            {"primary": "#007A3D", "text": "#FFFFFF"},
    "NORUEGA":         {"primary": "#EF2B2D", "text": "#FFFFFF"},

    # ── GRUPO J ──────────────────────────────────────────────
    "ARGENTINA":       {"primary": "#74ACDF", "text": "#FFFFFF"},
    "ARGELIA":         {"primary": "#006233", "text": "#FFFFFF"},
    "AUSTRIA":         {"primary": "#ED2939", "text": "#FFFFFF"},
    "JORDANIA":        {"primary": "#007A3D", "text": "#CE1126"},

    # ── GRUPO K ──────────────────────────────────────────────
    "PORTUGAL":        {"primary": "#006600", "text": "#FFFFFF"},
    "RD CONGO":        {"primary": "#007FFF", "text": "#FFFFFF"},
    "UZBEKISTAN":      {"primary": "#1EB53A", "text": "#FFFFFF"},
    "COLOMBIA":        {"primary": "#FCD116", "text": "#1A1A1A"},

    # ── GRUPO L ──────────────────────────────────────────────
    "INGLATERRA":      {"primary": "#CF2027", "text": "#FFFFFF"},
    "CROACIA":         {"primary": "#CC0000", "text": "#FFFFFF"},
    "GHANA":           {"primary": "#006B3F", "text": "#FCD116"},
    "PANAMA":          {"primary": "#DA121A", "text": "#FFFFFF"},
}

_DEFAULT = {"primary": "#2C3E50", "text": "#FFFFFF"}


def get_team_color(team: str) -> dict:
    return TEAM_COLORS.get(team.upper().strip(), _DEFAULT)


def team_chip_html(team: str, size: str = "normal") -> str:
    """Badge con el color del equipo. size = 'small' | 'normal' | 'large'"""
    c = get_team_color(team)
    sizes = {
        "small":  {"font": "0.72rem", "pad": "2px 8px",   "radius": "5px"},
        "normal": {"font": "0.88rem", "pad": "4px 12px",  "radius": "7px"},
        "large":  {"font": "1.05rem", "pad": "6px 16px",  "radius": "8px"},
    }
    s = sizes.get(size, sizes["normal"])
    return (
        f'<span style="background:{c["primary"]};color:{c["text"]};'
        f'padding:{s["pad"]};border-radius:{s["radius"]};font-weight:800;'
        f'font-size:{s["font"]};display:inline-block;letter-spacing:0.5px;">'
        f'{team}</span>'
    )


def match_card_html(
    team_home: str,
    team_away: str,
    date_str: str = "",
    time_str: str = "",
    venue: str = "",
    city: str = "",
    score_home=None,
    score_away=None,
    extra: str = "",
) -> str:
    """
    Tarjeta de partido completa con colores de cada equipo.
    extra: HTML opcional que se agrega al pie (por ej. puntos del prode).
    """
    ch = get_team_color(team_home)
    ca = get_team_color(team_away)

    if score_home is not None and score_away is not None:
        middle = (
            f'<span style="font-size:1.6rem;font-weight:900;color:#FFFFFF;'
            f'letter-spacing:2px;">{score_home}&nbsp;–&nbsp;{score_away}</span>'
        )
    else:
        middle = '<span style="font-size:0.85rem;color:#555;font-weight:700;letter-spacing:2px;">VS</span>'

    header_parts = []
    if date_str:
        header_parts.append(date_str)
    if time_str:
        header_parts.append(f"<b>{time_str} hs</b>")
    if venue:
        header_parts.append(f"📍 {venue}{', ' + city if city else ''}")
    header_html = (
        f'<div style="font-size:0.72rem;color:#8899AA;margin-bottom:0.6rem;'
        f'letter-spacing:0.5px;">{" &nbsp;·&nbsp; ".join(header_parts)}</div>'
        if header_parts else ""
    )

    extra_html = (
        f'<div style="margin-top:0.5rem;padding-top:0.5rem;border-top:1px solid #2C3E50;">'
        f'{extra}</div>'
        if extra else ""
    )

    return f"""
<div style="background:#1C2333;border-radius:12px;padding:0.9rem 1.2rem;
            margin:0.35rem 0;border:1px solid #2C3E50;">
  {header_html}
  <div style="display:flex;align-items:center;justify-content:space-between;gap:0.5rem;">
    <div style="flex:1;text-align:right;">
      <span style="background:{ch['primary']};color:{ch['text']};
        padding:5px 14px;border-radius:8px;font-weight:800;font-size:0.88rem;
        display:inline-block;letter-spacing:0.5px;">{team_home}</span>
    </div>
    <div style="flex:0 0 70px;text-align:center;">{middle}</div>
    <div style="flex:1;text-align:left;">
      <span style="background:{ca['primary']};color:{ca['text']};
        padding:5px 14px;border-radius:8px;font-weight:800;font-size:0.88rem;
        display:inline-block;letter-spacing:0.5px;">{team_away}</span>
    </div>
  </div>
  {extra_html}
</div>"""
