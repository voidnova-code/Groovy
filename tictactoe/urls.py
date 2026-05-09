from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render

from pages import views as page_views


def spa_index(request):
    return render(request, "index.html")


urlpatterns = [
    # Django admin
    path("admin/", admin.site.urls),

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
    path("admin/logs/", page_views.admin_logs, name="admin_logs"),

    # Export
    path("admin/export/users/", page_views.export_users, name="export_users"),
    path("admin/export/games/", page_views.export_games, name="export_games"),

    # API endpoints
    path("api/", include("game.urls")),

    # SPA entry
    path("", spa_index, name="home"),
]