# Smart Task Analyzer

## What
Mini app that scores tasks and returns them sorted by priority.

## How to run (local)
1. Create & activate virtualenv
2. pip install -r requirements.txt
3. python manage.py migrate
4. python manage.py runserver
5. Serve frontend (see frontend/README or open via simple http server)

## Algorithm summary
(Write 300-500 words explaining weights, urgency vs importance tradeoffs, overdue boost, quick-win logic, dependency handling, handling missing fields.)

## Tests
python manage.py test tasks

## Design decisions
- No auth
- Keep scoring function pure (testable)
- Frontend kept minimal
