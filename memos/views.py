from django.shortcuts import render
from rest_framework import viewsets , status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from memos.models import Memo
from memos.serializers import MemoCreateSerializer, MemoDetailSerializer, ApprovalLogSerializer , MemoApproveSerializer, MemoRejectSerializer
from memos.services import MemoService
# Create your views here.

class MemoViewSet(viewsets.ModelViewSet):
    """ Memo ViewSet to handle CRUD operations and approval actions for Memos. """
    permission_classes = [IsAuthenticated]
    queryset = Memo.objects.all()

    def get_queryset(self):
        return MemoService.get_user_memos(self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MemoCreateSerializer
        elif self.action == 'approve':
            return MemoApproveSerializer
        elif self.action == 'reject':
            return MemoRejectSerializer
        elif self.action == 'approval_logs':
            return ApprovalLogSerializer
        else:
            return MemoDetailSerializer
    
    @action(detail=True , methods=['POST'],
            serializer_class=MemoApproveSerializer)
    def approve(self , request , pk=None):
        memo = self.get_object()
        self.check_object_permissions(request, memo)  # Ensure user has permission to approve this memo
        context = self.get_serializer_context()
        context['memo'] = memo
        serializer = self.get_serializer(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Memo approved successfully."} , status=status.HTTP_200_OK)
    
    @action(detail=True , methods=['POST'],
            serializer_class=MemoRejectSerializer)
    def reject(self , request , pk=None):
        memo = self.get_object()
        self.check_object_permissions(request, memo)  # Ensure user has permission to reject this memo
        context = self.get_serializer_context()
        context['memo'] = memo
        serializer = self.get_serializer(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Memo rejected successfully."} , status=status.HTTP_200_OK)
    
    @action(detail=True , methods=['GET'] , serializer_class=ApprovalLogSerializer)
    def approval_logs(self , request , pk=None):
        memo = self.get_object()
        logs = MemoService.get_approval_logs_for_memo(memo)
        serializer = self.get_serializer(logs , many=True)
        return Response(serializer.data , status=status.HTTP_200_OK)
