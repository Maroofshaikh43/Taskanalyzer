# backend/urls.py
from django.contrib import admin
from django.urls import path, include
from . import frontend_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/tasks/', include('tasks.urls')),

    # Serve frontend
    path('', frontend_views.index, name='frontend_index'),                # /
    path('<path:path>', frontend_views.serve_file, name='frontend_files'), # /styles.css, /script.js, etc.
]
