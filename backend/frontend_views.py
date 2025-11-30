# backend/frontend_views.py
import os
from django.conf import settings
from django.http import FileResponse, Http404, HttpResponse
from mimetypes import guess_type

FRONTEND_DIR = os.path.join(settings.BASE_DIR, 'frontend')

def _safe_path(path):
    # Prevent directory traversal
    normalized = os.path.normpath(os.path.join(FRONTEND_DIR, path))
    if not normalized.startswith(FRONTEND_DIR):
        return None
    return normalized

def index(request):
    file_path = _safe_path('index.html')
    if file_path and os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), content_type='text/html')
    raise Http404("index.html not found")

def serve_file(request, path):
    file_path = _safe_path(path)
    if not file_path or not os.path.exists(file_path):
        raise Http404(path + " not found")
    content_type, _ = guess_type(file_path)
    if content_type is None:
        content_type = 'application/octet-stream'
    return FileResponse(open(file_path, 'rb'), content_type=content_type)
