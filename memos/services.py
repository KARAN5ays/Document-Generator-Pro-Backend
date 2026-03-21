from memos.models import Memo
from approvals.models import ApprovalChainLog

class MemoService:
    """ Service Class For Handling Business Logic Related To Memos """
    @staticmethod
    def get_user_memos(user):
        """ User can see memos they created, or memos belonging to their merchant (for approvers) """
        from django.db.models import Q
        if user.merchant:
            return Memo.objects.filter(Q(created_by=user) | Q(merchant=user.merchant)).select_related(
                'created_by', 'merchant', 'approval_chain'
            ).prefetch_related('approval_chain__actions__allowed_roles')
        else:
            return Memo.objects.filter(created_by=user).select_related(
                'created_by', 'merchant', 'approval_chain'
            ).prefetch_related('approval_chain__actions__allowed_roles')
    
    @staticmethod
    def get_approval_logs_for_memo(memo):
        """ Business rule approval logs for a memo are found by matching  the app_label and model_name  and the memo's idx"""
        return ApprovalChainLog.objects.filter(
            app_label = memo._meta.app_label,
            model = memo._meta.model_name,
            obj_idx = memo.idx).order_by('-created_at')