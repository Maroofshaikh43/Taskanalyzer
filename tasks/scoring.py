from datetime import date, datetime
from math import exp

def parse_date(d):
    if not d:
        return None
    if isinstance(d, date):
        return d
    try:
        return datetime.strptime(d, "%Y-%m-%d").date()
    except Exception:
        return None

def calculate_task_score(task_data, today=None, weights=None):
    """
    Returns a numeric score. Higher = higher priority.
    task_data: dict with keys: title, due_date (YYYY-MM-DD or date), importance (1-10), estimated_hours, dependencies(list)
    weights: optional dict to tune weights: {'urgency':x, 'importance':y, 'effort':z, 'dependency':w}
    """
    if today is None:
        today = date.today()
    if weights is None:
        weights = {'urgency': 1.5, 'importance': 5.0, 'effort': 1.0, 'dependency': 2.0, 'overdue_boost': 50}

    score = 0.0

    # --- Importance (scaled)
    importance = task_data.get('importance') or 5
    try:
        importance = max(1, min(10, int(importance)))
    except Exception:
        importance = 5
    score += importance * weights['importance']  # heavy weight

    # --- Urgency
    due = parse_date(task_data.get('due_date'))
    if due:
        days_until = (due - today).days
        if days_until < 0:
            # overdue -> big boost
            score += weights['overdue_boost']
            days_until = 0
        # urgency contribution: inverse with days, using a decay function
        # closer deadlines get higher contribution
        urgency_contrib = weights['urgency'] * (1.0 / (1 + days_until))
        score += urgency_contrib * 100  # scale to match importance magnitude
    else:
        # no due date -> small default
        score += 0

    # --- Effort (quick wins)
    est = task_data.get('estimated_hours')
    try:
        est = float(est)
    except Exception:
        est = 1.0
    # we prefer quick tasks: smaller estimated_hours gives bonus
    # Use a bounded function so very small times don't explode
    effort_bonus = weights['effort'] * (1.0 / (1.0 + est))
    score += effort_bonus * 20

    # --- Dependencies
    deps = task_data.get('dependencies') or []
    if isinstance(deps, (list, tuple)):
        dep_count = len(deps)
    else:
        dep_count = 0
    score += dep_count * weights['dependency'] * 5

    # final normalization: keep as float (caller can round)
    return round(score, 4)
