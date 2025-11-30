# tasks/serializers.py
from rest_framework import serializers
from .models import Task

class TaskInputSerializer(serializers.Serializer):
    title = serializers.CharField()
    due_date = serializers.DateField(required=False, allow_null=True)
    importance = serializers.IntegerField(required=False, min_value=1, max_value=10)
    estimated_hours = serializers.FloatField(required=False, min_value=0)
    dependencies = serializers.ListField(child=serializers.CharField(), required=False)

class TaskModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'due_date', 'importance', 'estimated_hours', 'dependencies']
