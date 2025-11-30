from django.contrib import admin

# Register your models here.
# tasks/admin.py
from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id','title','due_date','importance','estimated_hours')
    search_fields = ('title',)
    list_filter = ('importance',)
