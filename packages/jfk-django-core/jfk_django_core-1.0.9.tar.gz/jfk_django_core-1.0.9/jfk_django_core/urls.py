from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework import routers

from . import apis, viewsets

app_name = "jfk-django-core"

router = routers.DefaultRouter()
router.register(f"{app_name}/user", viewsets.UserViewSet, basename="user")

urlpatterns = [
    # Knox
    path("api/auth/login/", apis.TokenLoginView.as_view(), name="login"),
    path("api/auth/logout/", apis.TokenLogoutView.as_view(), name="logout"),
    path("api/auth/logoutall/", apis.TokenLogoutAllView.as_view(), name="logoutall"),
    # Swagger UI
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/swagger-ui/", SpectacularSwaggerView.as_view(), name="swagger-ui"),
    path("api/schema/redoc/", SpectacularRedocView.as_view(), name="redoc"),
    # Core
    path(f"api/{app_name}/healthcheck/", apis.HealthCheck.as_view(), name="healthcheck"),
]
