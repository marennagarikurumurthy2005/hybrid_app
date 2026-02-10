from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.http import HttpResponse

from core.db import get_db
from core.utils import utcnow

try:
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
except Exception:
    generate_latest = None
    CONTENT_TYPE_LATEST = "text/plain"


class HealthView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        ok = True
        try:
            db = get_db()
            db.command("ping")
        except Exception:
            ok = False
        return Response({"status": "ok" if ok else "degraded", "timestamp": utcnow().isoformat()})


class MetricsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        if not generate_latest:
            return HttpResponse("prometheus_client not installed", content_type="text/plain", status=501)
        data = generate_latest()
        return HttpResponse(data, content_type=CONTENT_TYPE_LATEST)
