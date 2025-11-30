# tasks/views.py (replace existing analyze_tasks & suggest_tasks definitions with these)

from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .serializers import TaskInputSerializer, TaskModelSerializer
from .scoring import calculate_task_score, parse_date
from .models import Task
from datetime import date
from django.db import transaction

# Helper (keep your normalize_task_input above or re-add if needed)
def normalize_task_input(raw):
    """
    Ensure keys exist and types are normalized:
    returns dict with title, due_date (iso or None), importance, estimated_hours, dependencies(list)
    """
    t = {}
    t['title'] = raw.get('title', '').strip() if raw.get('title') else ''
    dd = raw.get('due_date')
    # parse_date is imported at top of file; returns a date or None
    dt = parse_date(dd) if 'parse_date' in globals() else None
    t['due_date'] = dt.isoformat() if dt else None
    try:
        t['importance'] = int(raw.get('importance', 5))
    except Exception:
        t['importance'] = 5
    try:
        t['estimated_hours'] = float(raw.get('estimated_hours', 1))
    except Exception:
        t['estimated_hours'] = 1.0
    deps = raw.get('dependencies') or []
    if not isinstance(deps, (list, tuple)):
        deps = [deps]
    t['dependencies'] = list(deps)
    return t


@csrf_exempt
@api_view(['POST'])
@authentication_classes([])          # disable SessionAuthentication for this view
@permission_classes([AllowAny])      # allow anonymous access
def analyze_tasks(request):
    # (paste your current analyze_tasks body here, unchanged)
    # --- BEGIN body (keep existing logic) ---
    data = request.data
    want_save = False
    tasks_payload = None

    if isinstance(data, dict) and 'tasks' in data:
        tasks_payload = data['tasks']
        want_save = bool(data.get('save', False))
    elif isinstance(data, list):
        tasks_payload = data
    else:
        return Response({"error": "Expected tasks array or {tasks:[...], save:bool}"}, status=400)

    if not isinstance(tasks_payload, list):
        return Response({"error": "tasks must be an array"}, status=400)

    normalized = [normalize_task_input(t) for t in tasks_payload]

    results = []
    if want_save:
        keys = [(t['title'], t['due_date']) for t in normalized if t['title']]
        titles = list({k[0] for k in keys if k[0]})
        existing_qs = Task.objects.filter(title__in=titles)
        existing_map = {}
        for e in existing_qs:
            key = (e.title, e.due_date.isoformat() if e.due_date else None)
            existing_map[key] = e

        to_create = []
        to_update = []
        now_results = []
        for t in normalized:
            key = (t['title'], t['due_date'])
            score = calculate_task_score(t, today=date.today())
            if key in existing_map:
                obj = existing_map[key]
                changed = False
                if obj.importance != t['importance']:
                    obj.importance = t['importance']; changed = True
                if float(obj.estimated_hours) != float(t['estimated_hours']):
                    obj.estimated_hours = t['estimated_hours']; changed = True
                if (obj.dependencies or []) != t['dependencies']:
                    obj.dependencies = t['dependencies']; changed = True
                if changed:
                    to_update.append(obj)
                    action = 'updated'
                else:
                    action = 'unchanged'
                now_results.append({
                    'title': t['title'],
                    'due_date': t['due_date'],
                    'importance': t['importance'],
                    'estimated_hours': t['estimated_hours'],
                    'dependencies': t['dependencies'],
                    'score': score,
                    'action': action,
                    'id': obj.id
                })
            else:
                new_obj = Task(
                    title = t['title'],
                    due_date = t['due_date'],
                    importance = t['importance'],
                    estimated_hours = t['estimated_hours'],
                    dependencies = t['dependencies']
                )
                to_create.append(new_obj)
                now_results.append({
                    'title': t['title'],
                    'due_date': t['due_date'],
                    'importance': t['importance'],
                    'estimated_hours': t['estimated_hours'],
                    'dependencies': t['dependencies'],
                    'score': score,
                    'action': 'created',
                    'id': None
                })

        with transaction.atomic():
            if to_create:
                Task.objects.bulk_create(to_create)
            if to_update:
                Task.objects.bulk_update(to_update, ['importance','estimated_hours','dependencies'])

        if to_create:
            created_titles = [o.title for o in to_create]
            created_qs = Task.objects.filter(title__in=created_titles)
            created_map = {}
            for e in created_qs:
                key = (e.title, e.due_date.isoformat() if e.due_date else None)
                created_map.setdefault(key, []).append(e)
            for r in now_results:
                if r['action'] == 'created' and r['id'] is None:
                    key = (r['title'], r['due_date'])
                    lst = created_map.get(key, [])
                    if lst:
                        e = lst.pop(0)
                        r['id'] = e.id

        results = sorted(now_results, key=lambda x: x['score'], reverse=True)

    else:
        for t in normalized:
            score = calculate_task_score(t, today=date.today())
            results.append({**t, 'score': score})
        results = sorted(results, key=lambda x: x['score'], reverse=True)

    return Response(results)
    # --- END body ---

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([])          # disable SessionAuthentication for suggest too
@permission_classes([AllowAny])
def suggest_tasks(request):
    def explain_and_score(task):
        score = calculate_task_score(task, today=date.today())
        expl = {
            "importance": task.get('importance', 5),
            "estimated_hours": task.get('estimated_hours', 1),
            "dependencies": len(task.get('dependencies') or [])
        }
        try:
            d = parse_date(task.get('due_date'))
            expl['days_until_due'] = (d - date.today()).days if d else None
        except Exception:
            expl['days_until_due'] = None
        return score, expl

    tasks_list = []
    if request.method == 'POST':
        payload = request.data
        if isinstance(payload, dict) and 'tasks' in payload and isinstance(payload['tasks'], list):
            tasks_list = payload['tasks']
        elif isinstance(payload, list):
            tasks_list = payload
        else:
            return Response({"error": "POST expects a JSON array or {tasks:[...]}."}, status=400)
    else:
        qs = Task.objects.all()[:100]
        for t in qs:
            tasks_list.append({
                "id": t.id,
                "title": t.title,
                "due_date": t.due_date.isoformat() if t.due_date else None,
                "importance": t.importance,
                "estimated_hours": t.estimated_hours,
                "dependencies": t.dependencies or []
            })

    scored = []
    for t in tasks_list:
        score, expl = explain_and_score(t)
        entry = dict(t)
        entry['score'] = score
        entry['explanation'] = expl
        scored.append(entry)

    top3 = sorted(scored, key=lambda x: x.get('score', 0), reverse=True)[:3]
    return Response(top3)
