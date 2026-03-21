from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Merchant
from .serializers import MerchantSerializer

class MerchantViewSet(viewsets.ReadOnlyModelViewSet):
    """ ViewSet for viewing Merchants. ReadOnly means anyone authenticated can list them to select one. """
    permission_classes = [IsAuthenticated]
    queryset = Merchant.objects.filter(is_active=True).order_by('name')
    serializer_class = MerchantSerializer
