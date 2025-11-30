from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from .scoring import calculate_task_score
from datetime import date, timedelta

class ScoringTests(TestCase):
    def test_overdue_boost(self):
        t = {'title': 'old', 'due_date': (date.today() - timedelta(days=2)).isoformat(), 'importance': 5, 'estimated_hours': 2}
        s = calculate_task_score(t)
        self.assertTrue(s > 50)

    def test_quick_win_bonus(self):
        t1 = {'title': 'quick', 'due_date': (date.today() + timedelta(days=10)).isoformat(), 'importance': 5, 'estimated_hours': 0.5}
        t2 = {'title': 'slow', 'due_date': (date.today() + timedelta(days=10)).isoformat(), 'importance': 5, 'estimated_hours': 10}
        self.assertTrue(calculate_task_score(t1) > calculate_task_score(t2))

    def test_dependency_increases_score(self):
        t_no = {'title': 'a', 'due_date': (date.today() + timedelta(days=5)).isoformat(), 'importance': 5, 'estimated_hours': 2, 'dependencies': []}
        t_yes = {'title': 'b', 'due_date': (date.today() + timedelta(days=5)).isoformat(), 'importance': 5, 'estimated_hours': 2, 'dependencies': ['x']}
        self.assertTrue(calculate_task_score(t_yes) > calculate_task_score(t_no))
