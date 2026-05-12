"""
scoring.py - Motor de puntuacion del Prode Mundial 2026

Sistema de puntos:
- Fase de Grupos: 1pt resultado correcto (W/D/L), +1pt pleno (resultado exacto)
- Clasificados: 1-4pts segun acierto de posiciones
- Bonus: mejor 3ro (1pt), pleno de grupo (1pt)
- Playoffs: 1pt resultado 90min, +2pts pleno 90min, 1pt equipo que avanza
- Final: campeon correcto = 2pts (en vez de 1), MVP = 1pt
- Largo plazo: semifinalista 3pts, finalista +5pts, campeon +7pts
- Goleadores: 1ro 10pts, 2do 5pts, max 15pts
"""


def get_match_outcome(home_goals: int, away_goals: int) -> str:
    """Retorna 'H' (home win), 'A' (away win), o 'D' (draw)."""
    if home_goals > away_goals:
        return "H"
    elif home_goals < away_goals:
        return "A"
    return "D"


# ============================================================
# FASE DE GRUPOS - PUNTOS POR PARTIDO
# ============================================================
def score_group_match(
    pred_home: int, pred_away: int,
    real_home: int, real_away: int
) -> dict:
    """
    Calcula puntos de un partido de fase de grupos.
    Returns dict con detalle de puntos.
    """
    points = 0
    details = []

    if pred_home is None or pred_away is None:
        return {"points": 0, "details": ["Sin pronostico"]}

    pred_outcome = get_match_outcome(pred_home, pred_away)
    real_outcome = get_match_outcome(real_home, real_away)

    # 1pt por acertar resultado (W/D/L)
    if pred_outcome == real_outcome:
        points += 1
        details.append("Resultado correcto (+1)")

        # +1pt adicional por pleno (resultado exacto)
        if pred_home == real_home and pred_away == real_away:
            points += 1
            details.append("Pleno! (+1)")

    if not details:
        details.append("Fallo")

    return {"points": points, "details": details}


# ============================================================
# FASE DE GRUPOS - CLASIFICADOS Y POSICIONES
# ============================================================
def score_group_classification(
    pred_1st: str, pred_2nd: str,
    real_1st: str, real_2nd: str,
    pred_3rd: str = None,
    real_3rd: str = None,
    real_third_qualifies: bool = False,
) -> dict:
    """
    Calcula puntos por clasificados de un grupo.

    Args:
        pred_1st, pred_2nd: pronostico de 1ro y 2do
        real_1st, real_2nd: resultado real de 1ro y 2do
        pred_3rd: equipo que el jugador puso como 3ro que clasifica (None si no marco este grupo)
        real_3rd: equipo que realmente salio 3ro
        real_third_qualifies: si el 3ro de este grupo efectivamente clasifico

    Puntuacion 1ro/2do:
        4pts: ambos en orden exacto
        3pts: ambos correctos, invertidos
        2pts: un clasificado en posicion correcta
        2pts: ambos clasifican, diferente orden
        1pt: un clasificado entre top 2, otro orden

    Bonus Mejor Tercero: +1pt si acerto el equipo que sale 3ro Y ese 3ro clasifica
    Bonus Pleno de Grupo: +1pt si acerto TODOS los equipos que pasan (sin importar orden)
    """
    points = 0
    details = []

    if not pred_1st or not pred_2nd:
        return {"points": 0, "details": ["Sin pronostico de clasificados"]}

    # Normalizar
    p1 = pred_1st.upper().strip()
    p2 = pred_2nd.upper().strip()
    r1 = real_1st.upper().strip()
    r2 = real_2nd.upper().strip()

    both_in = {p1, p2} == {r1, r2}
    first_correct = (p1 == r1)
    second_correct = (p2 == r2)
    p1_in_top2 = p1 in {r1, r2}
    p2_in_top2 = p2 in {r1, r2}

    if first_correct and second_correct:
        points = 4
        details.append("1ro y 2do exactos! (+4)")
    elif both_in and p1 == r2 and p2 == r1:
        points = 3
        details.append("Clasificados correctos, orden invertido (+3)")
    elif first_correct or second_correct:
        points = 2
        details.append("Un clasificado en posicion correcta (+2)")
    elif both_in:
        points = 2
        details.append("Ambos clasifican, diferente orden (+2)")
    elif p1_in_top2 or p2_in_top2:
        points = 1
        details.append("Un clasificado entre top 2 (+1)")
    else:
        details.append("No acerto clasificados")

    # Bonus: Mejor Tercero (acertar equipo 3ro que clasifica)
    third_correct = False
    if pred_3rd and real_3rd and real_third_qualifies:
        p3 = pred_3rd.upper().strip()
        r3 = real_3rd.upper().strip()
        if p3 == r3:
            points += 1
            details.append("Mejor 3ro correcto! (+1)")
            third_correct = True

    # Bonus: Pleno de Grupo
    # Acertar TODOS los equipos que pasan del grupo, sin importar orden
    if real_third_qualifies:
        # Pasan 3 del grupo: necesita acertar 1ro+2do (cualquier orden) + equipo 3ro correcto
        if both_in and third_correct:
            points += 1
            details.append("Pleno de grupo! (+1)")
    else:
        # Pasan 2 del grupo: necesita acertar ambos clasificados (cualquier orden)
        if both_in:
            points += 1
            details.append("Pleno de grupo! (+1)")

    return {"points": points, "details": details}


# ============================================================
# PREDICCIONES A LARGO PLAZO (PODIO)
# ============================================================
def score_long_term_predictions(
    pred_champion: str,
    pred_finalist: str,
    pred_semi1: str,
    pred_semi2: str,
    real_champion: str = None,
    real_finalist: str = None,
    real_semi1: str = None,
    real_semi2: str = None,
) -> dict:
    """
    Calcula puntos por predicciones a largo plazo.
    Semifinalista: 3pts, Finalista: +5pts, Campeon: +7pts.
    Los puntos son acumulables (campeon = 3+5+7 = 15pts).
    """
    points = 0
    details = []

    if not real_champion:
        return {"points": 0, "details": ["Torneo no finalizado"]}

    # Los 4 semifinalistas reales
    real_semis = {
        s.upper().strip() for s in [real_champion, real_finalist, real_semi1, real_semi2]
        if s
    }
    # Los 2 finalistas reales
    real_finals = set()
    if real_champion:
        real_finals.add(real_champion.upper().strip())
    if real_finalist:
        real_finals.add(real_finalist.upper().strip())

    real_champ = real_champion.upper().strip() if real_champion else None

    # Evaluar cada prediccion del jugador
    predictions = {
        "champion": pred_champion,
        "finalist": pred_finalist,
        "semi1": pred_semi1,
        "semi2": pred_semi2,
    }

    for label, pred in predictions.items():
        if not pred:
            continue
        p = pred.upper().strip()

        if p == real_champ:
            # Acerto al campeon: 3 (semi) + 5 (final) + 7 (campeon) = 15
            points += 15
            details.append(f"{pred}: Campeon! (+15)")
        elif p in real_finals:
            # Acerto finalista: 3 (semi) + 5 (final) = 8
            points += 8
            details.append(f"{pred}: Finalista (+8)")
        elif p in real_semis:
            # Acerto semifinalista: 3
            points += 3
            details.append(f"{pred}: Semifinalista (+3)")

    if not details:
        details.append("No acerto podio")

    return {"points": points, "details": details}


# ============================================================
# GOLEADORES
# ============================================================
def _names_match(a: str, b: str) -> bool:
    a, b = a.upper().strip(), b.upper().strip()
    if not a or not b:
        return False
    if a == b:
        return True
    if a in b or b in a:
        return True
    return bool(set(a.split()) & set(b.split()))


def _in_name_group(player: str, name_set: set) -> bool:
    return any(_names_match(player, n) for n in name_set)


def score_scorers(
    pred_scorer1: str,
    pred_scorer2: str,
    real_scorers: list[dict],  # [{"name": "MBAPPE", "goals": 9, "rank": 1}, ...]
) -> dict:
    """
    Calcula puntos por goleadores.

    real_scorers: lista ordenada de goleadores con su ranking.
    Reglas:
    - 1er goleador: 10pts
    - 2do goleador: 5pts
    - Max 15pts entre ambos jugadores elegidos
    - Si hay empate en 1er puesto, cada co-lider suma 10pts
      (pero si tenes 2 co-lideres, uno suma 10 y otro 5)
    - Si hay empate en 1er puesto, el siguiente NO suma como 2do
    - Si hay empate en 2do puesto, todos suman 5pts
      (pero si tenes 2 en 2do, solo uno suma 5pts)
    """
    points = 0
    details = []

    if not pred_scorer1 or not real_scorers:
        return {"points": 0, "details": ["Sin datos de goleadores"]}

    p1 = pred_scorer1.upper().strip()
    p2 = pred_scorer2.upper().strip() if pred_scorer2 else ""

    # Determinar quienes son 1ros y 2dos
    first_place_goals = real_scorers[0]["goals"] if real_scorers else 0
    first_place = [s for s in real_scorers if s["goals"] == first_place_goals]
    first_place_names = {s["name"].upper().strip() for s in first_place}

    # 2do puesto: siguiente nivel de goles (solo si no hay empate masivo en 1ro)
    second_place_names = set()
    if len(first_place) < len(real_scorers):
        second_goals = max(
            s["goals"] for s in real_scorers if s["goals"] < first_place_goals
        ) if any(s["goals"] < first_place_goals for s in real_scorers) else 0
        if second_goals > 0 and len(first_place) == 1:
            # Solo hay 2do puesto si hay UN solo lider
            second_place = [s for s in real_scorers if s["goals"] == second_goals]
            second_place_names = {s["name"].upper().strip() for s in second_place}

    my_players = [p1]
    if p2:
        my_players.append(p2)

    scored_as_first = False
    scored_as_second = False

    for player in my_players:
        in_first = _in_name_group(player, first_place_names)
        in_second = _in_name_group(player, second_place_names)
        if in_first and not scored_as_first:
            if len(first_place_names) == 1:
                points += 10
                details.append(f"{player}: Goleador 1ro (+10)")
            else:
                if not scored_as_first:
                    points += 10
                    details.append(f"{player}: Co-goleador 1ro (+10)")
                    scored_as_first = True
                    continue
            scored_as_first = True
        elif in_first and scored_as_first:
            points += 5
            details.append(f"{player}: Co-goleador 1ro (2do jugador, +5)")
            scored_as_second = True
        elif in_second and not scored_as_second:
            points += 5
            details.append(f"{player}: Goleador 2do (+5)")
            scored_as_second = True

    # Cap a 15 puntos
    if points > 15:
        points = 15
        details.append("(Max 15pts aplicado)")

    if not details:
        details.append("No acerto goleadores")

    return {"points": points, "details": details}


# ============================================================
# PLAYOFFS - PUNTOS POR PARTIDO
# ============================================================
def score_playoff_match(
    pred_home: int, pred_away: int, pred_advances: str,
    real_home: int, real_away: int, real_advances: str,
    is_final: bool = False
) -> dict:
    """
    Calcula puntos de un partido de playoffs (90 minutos).

    - 1pt por acertar resultado 90min (W/D/L)
    - +2pts por pleno 90min (resultado exacto)
    - 1pt por acertar equipo que avanza (2pts si es la final)
    - MVP de final: se calcula aparte
    """
    points = 0
    details = []

    if pred_home is None or pred_away is None:
        return {"points": 0, "details": ["Sin pronostico"]}

    pred_outcome = get_match_outcome(pred_home, pred_away)
    real_outcome = get_match_outcome(real_home, real_away)

    # 1pt por resultado correcto 90min
    if pred_outcome == real_outcome:
        points += 1
        details.append("Resultado 90min correcto (+1)")

        # +2pts por pleno 90min
        if pred_home == real_home and pred_away == real_away:
            points += 2
            details.append("Pleno 90min! (+2)")

    # Equipo que avanza
    if pred_advances and real_advances:
        pa = pred_advances.upper().strip()
        ra = real_advances.upper().strip()
        if pa == ra:
            if is_final:
                points += 2
                details.append("Campeon correcto! (+2)")
            else:
                points += 1
                details.append("Equipo que avanza correcto (+1)")

    if not details:
        details.append("Fallo")

    return {"points": points, "details": details}


# ============================================================
# MVP DE LA FINAL
# ============================================================
def score_final_mvp(pred_mvp: str, real_mvp: str) -> dict:
    """1 punto por acertar MVP de la final."""
    if pred_mvp and real_mvp:
        if pred_mvp.upper().strip() == real_mvp.upper().strip():
            return {"points": 1, "details": ["MVP de la Final! (+1)"]}
    return {"points": 0, "details": ["No acerto MVP"]}


# ============================================================
# CALCULO TOTAL DE UN JUGADOR
# ============================================================
def calculate_total_score(
    group_match_scores: list[dict],
    group_classification_scores: list[dict],
    long_term_score: dict,
    scorer_score: dict,
    playoff_match_scores: list[dict],
    mvp_score: dict,
) -> dict:
    """
    Suma total de puntos de un jugador.
    """
    total = 0
    breakdown = {
        "grupos_partidos": 0,
        "grupos_clasificados": 0,
        "largo_plazo": 0,
        "goleadores": 0,
        "playoffs": 0,
        "mvp_final": 0,
    }

    for s in group_match_scores:
        breakdown["grupos_partidos"] += s["points"]
    for s in group_classification_scores:
        breakdown["grupos_clasificados"] += s["points"]
    breakdown["largo_plazo"] = long_term_score["points"]
    breakdown["goleadores"] = scorer_score["points"]
    for s in playoff_match_scores:
        breakdown["playoffs"] += s["points"]
    breakdown["mvp_final"] = mvp_score["points"]

    total = sum(breakdown.values())

    return {"total": total, "breakdown": breakdown}


# ============================================================
# TABLA DE POSICIONES DE GRUPO (para determinar clasificados)
# ============================================================
def _head_to_head_record(team_a: str, team_b: str, matches: list[dict]) -> tuple:
    """
    Calcula record directo entre dos equipos.
    Returns (pts_a, pts_b, gd_a, gf_a) del enfrentamiento directo.
    """
    pts_a = 0
    pts_b = 0
    gf_a = 0
    gc_a = 0

    for m in matches:
        th = m["team_home"]
        ta = m["team_away"]
        hg = m["home_goals"]
        ag = m["away_goals"]

        if hg is None or ag is None:
            continue

        if th == team_a and ta == team_b:
            gf_a += hg
            gc_a += ag
            if hg > ag:
                pts_a += 3
            elif hg < ag:
                pts_b += 3
            else:
                pts_a += 1
                pts_b += 1
        elif th == team_b and ta == team_a:
            gf_a += ag
            gc_a += hg
            if ag > hg:
                pts_a += 3
            elif ag < hg:
                pts_b += 3
            else:
                pts_a += 1
                pts_b += 1

    return (pts_a, pts_b, gf_a - gc_a, gf_a)


def calculate_group_standings(matches_with_results: list[dict]) -> list[dict]:
    """
    Calcula tabla de posiciones de un grupo.

    matches_with_results: lista de dicts con:
        {"team_home", "team_away", "home_goals", "away_goals"}

    Criterios de desempate (formato olimpico FIFA):
    1. Puntos totales
    2. Diferencia de gol general
    3. Goles a favor general
    4. Enfrentamiento directo (puntos, DG, GF)

    Returns: lista ordenada de dicts con:
        {"team", "pts", "gf", "gc", "gd", "played"}
    """
    teams = {}

    for m in matches_with_results:
        th = m["team_home"]
        ta = m["team_away"]
        hg = m["home_goals"]
        ag = m["away_goals"]

        if hg is None or ag is None:
            continue

        for t in [th, ta]:
            if t not in teams:
                teams[t] = {"team": t, "pts": 0, "gf": 0, "gc": 0, "gd": 0, "played": 0}

        teams[th]["played"] += 1
        teams[ta]["played"] += 1
        teams[th]["gf"] += hg
        teams[th]["gc"] += ag
        teams[ta]["gf"] += ag
        teams[ta]["gc"] += hg

        if hg > ag:
            teams[th]["pts"] += 3
        elif hg < ag:
            teams[ta]["pts"] += 3
        else:
            teams[th]["pts"] += 1
            teams[ta]["pts"] += 1

    for t in teams.values():
        t["gd"] = t["gf"] - t["gc"]

    # Ordenar con desempate por enfrentamiento directo
    import functools

    def compare_teams(a, b):
        """Comparador con desempate head-to-head."""
        # 1. Puntos
        if a["pts"] != b["pts"]:
            return b["pts"] - a["pts"]
        # 2. Diferencia de gol general
        if a["gd"] != b["gd"]:
            return b["gd"] - a["gd"]
        # 3. Goles a favor general
        if a["gf"] != b["gf"]:
            return b["gf"] - a["gf"]
        # 4. Enfrentamiento directo
        h2h = _head_to_head_record(a["team"], b["team"], matches_with_results)
        pts_a, pts_b, gd_a, gf_a = h2h
        if pts_a != pts_b:
            return pts_b - pts_a
        if gd_a != 0:
            return -gd_a  # negativo porque gd_a positivo = a gana
        return 0

    standings = sorted(
        teams.values(),
        key=functools.cmp_to_key(compare_teams)
    )

    return standings
