from django.db import models
# tasks/models.py (modify Task class)
class Task(models.Model):
    title = models.CharField(max_length=200)
    due_date = models.DateField(null=True, blank=True)
    importance = models.IntegerField(default=5)  # 1-10
    estimated_hours = models.FloatField(default=1)
    dependencies = models.JSONField(default=list, blank=True)

    class Meta:
        unique_together = ('title', 'due_date')  # optional but useful
