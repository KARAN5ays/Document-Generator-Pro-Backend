from memos.models import Memo
from approvals.models import ApprovalChainLog
from permission.constants import Role as ROLE


# Roles that are allowed to see ALL memos in their organisation
PRIVILEGED_ROLES = [
    ROLE.MANAGER.value,
    ROLE.FINANCE.value,
    ROLE.DIRECTOR.value,
    ROLE.SUPERUSER.value,
]


class MemoService:
    """Service Class For Handling Business Logic Related To Memos"""

    @staticmethod
    def get_user_memos(user):
        """
        Memo visibility rules:
          - Privileged roles (Manager, Finance, Director, Superuser) → all memos in their org.
          - Every other user → only memos they personally created.
        """
        base_qs = Memo.objects.select_related(
            'created_by', 'merchant', 'approval_chain'
        ).prefetch_related('approval_chain__actions__allowed_roles')

        """Priveleged users see all memos in their merchant org"""
        if user.merchant and user.iss(PRIVILEGED_ROLES):
            return base_qs.filter(merchant=user.merchant)

        """Non priveleged users see only memos they created"""
        return base_qs.filter(created_by=user)
    
    @staticmethod
    def get_approval_logs_for_memo(memo):
        """ Business rule approval logs for a memo are found by matching  the app_label and model_name  and the memo's idx"""
        return ApprovalChainLog.objects.filter(
            app_label = memo._meta.app_label,
            model = memo._meta.model_name,
            obj_idx = memo.idx).order_by('-created_at')