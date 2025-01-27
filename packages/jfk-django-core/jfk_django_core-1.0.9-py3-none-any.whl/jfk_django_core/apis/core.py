import logging

from drf_spectacular.utils import OpenApiTypes, extend_schema
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

log = logging.getLogger(__name__)


class HealthCheck(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    @extend_schema(
        operation_id="healthcheck",
        request=OpenApiTypes.OBJECT,
    )
    def head(self, request, format=None) -> Response:
        try:
            return Response(status=status.HTTP_200_OK)
        except Exception:
            log.exception("HealthCheck Exception")
            return Response("Unknown Error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
