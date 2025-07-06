from django.contrib.auth.views import LoginView, LogoutView
from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from users.apps import UsersConfig
from users.views import UserProfileViewSet

app_name = UsersConfig.name


router = DefaultRouter()
router.register(r"users", UserProfileViewSet, basename="user")

urlpatterns = [
    path("", include(router.urls)),
    path("logout/", LogoutView.as_view(next_page="mailings:start"), name="logout"),
    path("api-token-auth/", obtain_auth_token, name="api_token_auth"),
] + router.urls
