"""
Vues pour servir la maquette Admin Frontend (admin_frontend/) — Option A :
- Page de connexion (index.html) et Admin Console (admin_console.html) intégrées au backend.
"""
import mimetypes
from pathlib import Path

from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.shortcuts import redirect


def _admin_frontend_base():
    return Path(settings.BASE_DIR) / "admin_frontend"


def _read_html_safe(file_path):
    """Lit un fichier HTML en UTF-8. Les octets invalides sont remplacés (évite Ã© au lieu de é)."""
    with open(file_path, "rb") as f:
        raw = f.read()
    return raw.decode("utf-8", errors="replace")


def admin_login_maquette(request):
    """Sert la page de connexion maquette (admin_frontend/index.html). Depuis Django, le lien « Se connecter » mène vers /admin-console/."""
    base = _admin_frontend_base()
    index = base / "index.html"
    if not index.is_file():
        raise Http404("admin_frontend/index.html introuvable")
    content = _read_html_safe(index)
    # Quand on est servi par Django, faire pointer le bouton vers l'URL protégée
    content = content.replace('href="admin_console.html"', 'href="/admin-console/"')
    content = content.replace("window.location.href = 'admin_console.html'", "window.location.href = '/admin-console/'")
    return HttpResponse(content, content_type="text/html; charset=utf-8")


@login_required(login_url="/admin/")
def admin_console(request):
    """Sert l'Admin Console SPA (admin_frontend/admin_console.html). Réservé aux utilisateurs connectés."""
    base = _admin_frontend_base()
    console = base / "admin_console.html"
    if not console.is_file():
        raise Http404("admin_frontend/admin_console.html introuvable")
    content = _read_html_safe(console)
    return HttpResponse(content, content_type="text/html; charset=utf-8")


@login_required(login_url="/admin/login/")
def admin_console_logout(request):
    """Déconnexion depuis l'Admin Console ; redirige vers la page de connexion admin."""
    logout(request)
    return redirect("/admin/login/")


def admin_console_assets(request, path):
    """Sert les assets de l'Admin Console (admin_frontend/)."""
    base = _admin_frontend_base()
    file_path = (base / path).resolve()
    # Security check: ensure the resolved path is within admin_frontend
    if not str(file_path).startswith(str(base.resolve())):
        raise Http404(f"Access denied: {path}")
    if not file_path.is_file():
        raise Http404(f"Asset introuvable: {path}")
    content_type, _ = mimetypes.guess_type(str(file_path))
    with open(file_path, "rb") as f:
        return HttpResponse(f.read(), content_type=content_type or "application/octet-stream")


# Rétrocompatibilité : noms utilisés ailleurs
def admin_frontend_index(request):
    """Alias vers admin_login_maquette."""
    return admin_login_maquette(request)


def admin_frontend_assets(request, path):
    """Alias vers admin_console_assets."""
    return admin_console_assets(request, path)
