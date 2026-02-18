from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from backendapp.models import Document
from backendapp.serializers import DocumentListSerializer

class DashboardAnalyticsView(APIView):
    """
    Returns analytics data for the user's dashboard.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_documents = Document.objects.select_related('document_type').filter(issued_by=request.user)
        total_documents = user_documents.count()
        verified_documents = user_documents.filter(status='valid').count()
        
        # Get recent documents (last 5)
        recent_documents = user_documents.order_by('-created_at')[:5]
        
        # Generate real trend data for the last 6 months
        from django.db.models import Count
        from django.db.models.functions import TruncMonth
        from django.utils import timezone
        import datetime

        six_months_ago = timezone.now() - datetime.timedelta(days=180)
        
        trends_query = user_documents.filter(created_at__gte=six_months_ago) \
            .annotate(month=TruncMonth('created_at')) \
            .values('month') \
            .annotate(count=Count('id')) \
            .order_by('month')

        trends = []
        for entry in trends_query:
            trends.append({
                "month": entry['month'].strftime('%b'),
                "count": entry['count']
            })
        
        # If no trends, provide at least the current month with 0 if needed or leave empty
        # The frontend handles empty array with a nice placeholder.

        return Response({
            "total_documents": total_documents,
            "verified_documents": verified_documents,
            "active_users": 1,  # Current user
            "verification_alerts": user_documents.filter(status='revoked').count(),
            "trends": trends,
            "recent_documents": DocumentListSerializer(recent_documents, many=True).data,
        })

class VerificationStatsView(APIView):
    """
    Returns statistics about document statuses (valid vs revoked).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_documents = Document.objects.select_related('document_type').filter(issued_by=request.user)
        valid_count = user_documents.filter(status='valid').count()
        revoked_count = user_documents.filter(status='revoked').count()
        
        # Get recently verified (mock or actually track last verified)
        # For now, let's just return recently created documents
        recent = user_documents.order_by('-created_at')[:5]
        
        return Response({
            "valid": valid_count,
            "revoked": revoked_count,
            "total": valid_count + revoked_count,
            "total_verified": valid_count + revoked_count,
            "recently_verified": DocumentListSerializer(recent, many=True).data
        })
