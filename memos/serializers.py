from rest_framework import serializers
from memos.models import Memo
from approvals.models import ApprovalChainLog
from django.utils import timezone

class MemoCreateSerializer(serializers.ModelSerializer):
    """ Serializer for creating a new Memo """
    class Meta:
        model = Memo
        fields = [
            "title",
            "amount",
            "from_department",
            "to_department",
            "subject",
            "purpose",
            "background",
            "memo_type",
            "reference_number",
            "created_by",
            "merchant",
        ]

        read_only_fields = ["reference_number" , "created_by"]

    def create(self, validated_data):
        """ Override create method to set created_by from context. Merchant is provided by the frontend. """
        user = self.context['request'].user
        memo = Memo.objects.create(
            created_by=user,
            **validated_data
        )
        # Assign approval chain based on memo type
        approval_chain = memo._get_approval_chain()
        if not approval_chain:
            raise serializers.ValidationError("No approval chain configured for this memo type.")
        memo.approval_chain = approval_chain
        memo.save()
        return memo

class MemoDetailSerializer(serializers.ModelSerializer):
    "Detailed View of Memo With Approval Info"

    approval_status = serializers.CharField(source='get_approval_status_display', read_only=True)
    last_remarks = serializers.SerializerMethodField()
    next_action = serializers.SerializerMethodField()

    class Meta:
        model = Memo
        fields = [
            "id",
            "title",
            "amount",
            "from_department",
            "to_department",
            "subject",
            "purpose",
            "background",
            "memo_type",
            "reference_number",
            "merchant",
            "created_by",
            'created_at',
            'last_remarks',
            'next_action',
            "approval_status",
        ]

    def get_last_remarks(self, obj):
        """ Get The Most Recent Approval Log Remarks"""
        return obj.get_last_remark()    
    
    def get_next_action(self, obj):
        """Get The Next Action Required For This Memo"""
        next_action, _ = obj.next_action_and_last_log
        if not next_action:
            return None
            
        roles = []
        """ Optimization: If the approval chain and its actions are prefetched, we can avoid extra queries to fetch allowed roles for the next action. This is especially beneficial when listing memos with their next actions, as it prevents N+1 query issues."""
        if getattr(obj, 'approval_chain', None): 
            try:
                prefetched_action = next(a for a in obj.approval_chain.actions.all() if a.id == next_action.id)
                roles = [role.name for role in prefetched_action.allowed_roles.all()]
            except (StopIteration, AttributeError):
                roles = [role.name for role in next_action.allowed_roles.all()]
        else:
            roles = [role.name for role in next_action.allowed_roles.all()]
            
        return {
            "id": next_action.id,
            "name": next_action.title,
            "role": roles
        }
    
class ApprovalLogSerializer(serializers.ModelSerializer):
    """ Serializer for Approval Logs related to a Memo """
    actor_name = serializers.CharField(source='actor.display_name', read_only=True)
    action = serializers.CharField(source='approval_action.title', read_only=True)

    class Meta:
        model = ApprovalChainLog
        fields = [
            "id",
            "actor_name",
            "action",
            "remarks",
            "created_at",
        ]

class MemoApproveSerializer(serializers.Serializer):
    """ Used When User Clicks Approve"""
    remarks = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        """ Validate that the user can approve this memo """
        request = self.context['request']
        memo = self.context['memo']
        if not memo._can_approve(request.user):
            raise serializers.ValidationError("You do not have permission to approve this memo.")
        return data
    
    def save(self, **kwargs):
        """ Perform The Approve Action """
        request = self.context['request']
        memo = self.context['memo']
        remarks = self.validated_data.get('remarks', '')
        memo.approve(user=request.user , remarks= remarks)
        return memo

class MemoRejectSerializer(serializers.Serializer):
    """used when User clicks reject"""
    remarks = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        """ Validate that the user can reject this memo """
        request = self.context['request']
        memo = self.context['memo']
        if not memo._can_approve(request.user):
            raise serializers.ValidationError("You do not have permission to reject this memo.")
        return data

    def save(self, **kwargs):
        """ Perform The Reject Action """
        request = self.context['request']
        memo = self.context['memo']
        remarks = self.validated_data.get('remarks', '')
        memo.reject(user=request.user , remarks= remarks)
        return memo