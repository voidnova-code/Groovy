from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"rooms", views.GameRoomViewSet, basename="game-room")

urlpatterns = [
    path("auth/register/", views.register, name="register"),
    path("auth/login/", views.login, name="login"),
    path("auth/logout/", views.logout, name="logout"),
    path("auth/me/", views.get_current_user, name="current-user"),
    path("auth/razorpay-key/", views.get_razorpay_key, name="razorpay-key"),
    # Google OAuth endpoints
    path("auth/google/config/", views.get_google_auth_config, name="google-auth-config"),
    path("auth/google/callback/", views.google_auth_callback, name="google-auth-callback"),
    path("auth/google/link/", views.link_google_account, name="link-google-account"),
    path("", include(router.urls)),
]