from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("admin-login/", views.AdminLoginView.as_view(), name="admin_login"),
    path("google-login/", views.GoogleLoginView.as_view(), name="google_login"),
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
]
