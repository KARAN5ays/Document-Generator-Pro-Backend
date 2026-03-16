"""
Template Builder configuration API. Serves dynamic config from backend
so changes can be made without deploying frontend.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from backendapp.template_builder_config import get_template_builder_config


class TemplateBuilderConfigView(APIView):
    """Return template builder configuration. Edit template_builder_config.py to change behavior."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        config = get_template_builder_config()
        return Response(config)
