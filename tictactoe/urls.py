from django.urls import path, include
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth import views as auth_views
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import authenticate, login, logout as auth_logout

from pages import views as page_views


def spa_index(request):
    return render(request, "index.html")


def admin_index(request):
    """Route /admin/ to the custom admin experience."""
    if request.user.is_authenticated and request.user.is_superuser:
        return HttpResponseRedirect("/admin/dashboard/")
    return HttpResponseRedirect("/admin/login/")


@csrf_protect
def admin_login(request):
    """Custom admin login page with session-based auth"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_superuser:
            if request.user.is_authenticated:
                auth_logout(request)
            login(request, user)
            next_url = request.POST.get('next', '/admin/dashboard/')
            if next_url != '/admin/dashboard/':
                next_url = '/admin/dashboard/'
            return HttpResponseRedirect(next_url)
        else:
            return render(request, 'admin/login.html', {'error': 'Invalid admin credentials'})

    if request.user.is_authenticated:
        if request.user.is_superuser:
            return HttpResponseRedirect("/admin/dashboard/")
        return render(request, 'admin/login.html', {'error': 'You are logged in as a non-admin user. Sign in with a superuser account.'})

    return render(request, 'admin/login.html')


urlpatterns = [
    # Handle login redirect
    path("accounts/login/", admin_login, name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(next_page="/"), name="logout"),

    # Admin login
    path("admin/login/", admin_login, name="admin_login"),

    # Redirect root /admin/
    path("admin/", admin_index),

    # Custom admin panel
    path("admin/dashboard/", page_views.admin_dashboard, name="admin_dashboard"),
    path("admin/users/", page_views.admin_users, name="admin_users"),
    path("admin/user/create/", page_views.admin_create_user, name="admin_create_user"),
    path("admin/user/<int:user_id>/", page_views.admin_edit_user, name="admin_edit_user"),
    path("admin/user/delete/<int:user_id>/", page_views.delete_user, name="admin_delete_user"),
    path("admin/games/", page_views.admin_games, name="admin_games"),
    path("admin/game/<int:game_id>/", page_views.admin_game_detail, name="admin_game_detail"),
    path("admin/game/delete/<int:game_id>/", page_views.delete_game, name="admin_delete_game"),
    path("admin/feedbacks/", page_views.admin_feedbacks, name="admin_feedbacks"),
    path("admin/settings/", page_views.admin_settings, name="admin_settings"),
    path("admin/clear-data/", page_views.admin_clear_data, name="admin_clear_data"),
    path("admin/logs/", page_views.admin_logs, name="admin_logs"),

    # Export
    path("admin/export/users/", page_views.export_users, name="export_users"),
    path("admin/export/games/", page_views.export_games, name="export_games"),

    # API endpoints
    path("api/", include("game.urls")),

    # SPA entry
    path("", spa_index, name="home"),
]