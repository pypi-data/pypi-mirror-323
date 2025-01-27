"""JFK-Django-Core Apis."""

from knox.auth import TokenAuthentication
from rest_framework import permissions
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.views import APIView

from .core import *  # noqa: F403
from .jfk_authentication import *  # noqa: F403


class BaseAPIView(APIView):
    """Custom API View for all API Views in this file."""

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [SessionAuthentication, TokenAuthentication, BasicAuthentication]
