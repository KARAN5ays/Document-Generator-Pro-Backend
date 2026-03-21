from django.apps import apps
from django.core.cache import cache
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property

from helpers.exceptions import SilkroadException
from helpers.models import BaseModel
from permission.constants import Role as ROLE
from permission.models import Role
from django.conf import settings


class ApprovalChain(BaseModel):
    merchant = models.ForeignKey(
        'autho.Merchant',
        on_delete=models.PROTECT,
        related_name="approval_chains",
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=100, db_index=True)
    conditions = models.JSONField(default=dict)
    """
    Conditions Format [Subject to Change in Future]:
    For now the field value is exact match. In future we can add more operators like `__gt`, `__lt`, `__contains` etc.

    app:
        model:
            field1: value1
            field2: value2
        model2:
            field1: value1
            field2: value2
    """
    ttl = models.PositiveIntegerField(null=True, blank=True, help_text="Expires in seconds")

    class Meta:
        verbose_name = "Approval Chain"
        verbose_name_plural = "Approval Chains"

    def __str__(self):
        return f"{self.title} -> {self.merchant or 'Default'}"

    def is_eligible(self, obj):
        app = obj._meta.app_label
        if app not in self.conditions:
            return False

        model = obj._meta.model_name
        if model not in self.conditions[app]:
            return False

        for field, value in self.conditions[app][model].items():
            if getattr(obj, field) != value:
                return False

        return True


class ApprovalChainAction(BaseModel):
    title = models.CharField(max_length=100, db_index=True)
    approval_chain = models.ForeignKey(ApprovalChain, on_delete=models.PROTECT, related_name="actions")
    allowed_roles = models.ManyToManyField(Role, related_name="+", blank=True)
    allowed_actors = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="+", blank=True)
    ttl = models.PositiveIntegerField(null=True, blank=True, help_text="Expires in seconds")
    is_first = models.BooleanField(default=False)
    next_action = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        related_name="prev_actions",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Approval Chain Action"
        verbose_name_plural = "Approval Chain Actions"

    def __str__(self):
        return self.title

    def clean(self):
        if self.is_first and self.approval_chain.actions.filter(is_first=True).exclude(id=self.id).exists():
            raise SilkroadException("There can only be one first action in an approval chain.")

    def can_take_action(self, user):
        cache_key = f"can_take_approval_chain_action_{user.idx}:{self.idx}"
        try:
            is_allowed = cache.get(cache_key)
            is_cache_available = True
        except Exception:
            is_allowed = None
            is_cache_available = False

        if is_allowed is None:
            if self.allowed_actors.exists():
                is_allowed = user in self.allowed_actors.all() and self.approval_chain.merchant == user.merchant
            elif self.allowed_roles.exists():
                role_names = self.allowed_roles.values_list("name", flat=True)
                check1 = user.iss(role_names)
                check2 = self.approval_chain.merchant is None
                check3 = self.approval_chain.merchant == user.merchant
                is_allowed = check1 and (check2 or check3)
            else:
                is_allowed = False

            if is_cache_available:
                cache.set(cache_key, is_allowed, timeout=60)

        return is_allowed

    def proceed_to_next_action(self, user, obj, remarks=None, last_log=None):
        if not self.can_take_action(user):
            raise SilkroadException("You are not allowed to take this action.")

        ApprovalChainLog.objects.create(
            merchant=self.approval_chain.merchant,
            approval_chain=self.approval_chain,
            approval_action=self,
            app_label=obj._meta.app_label,
            model=obj._meta.model_name,
            obj_idx=obj.idx,
            actor=user,
            remarks=remarks,
            next_approval_action=self.next_action,
            previous_log_in_chain=last_log,
        )

        return self.next_action is None


class ApprovalChainLog(BaseModel):
    merchant = models.ForeignKey(
        'autho.Merchant',
        on_delete=models.PROTECT,
        related_name="approval_chain_logs",
        null=True,
        blank=True,
    )
    approval_chain = models.ForeignKey(ApprovalChain, on_delete=models.PROTECT, related_name="logs")
    approval_action = models.ForeignKey(ApprovalChainAction, on_delete=models.PROTECT, related_name="logs")
    app_label = models.CharField(max_length=100, db_index=True)
    model = models.CharField(max_length=100, db_index=True)
    obj_idx = models.CharField(max_length=20, db_index=True)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="approval_chain_logs")
    remarks = models.TextField(blank=True)
    next_approval_action = models.ForeignKey(
        ApprovalChainAction,
        on_delete=models.PROTECT,
        related_name="next_logs",
        null=True,
        blank=True,
    )
    previous_log_in_chain = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        related_name="next_logs_in_chain",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Approval Chain Log"
        verbose_name_plural = "Approval Chain Logs"

    def __str__(self):
        return self.idx

    def get_obj(self):
        return apps.get_model(self.app_label, self.model).objects.get(idx=self.obj_idx)


class ApprovalChainMixin(models.Model):
    """
    This is a model mixin that can be used to implement aproval chain logics to any model.

    Must Overiride the commit() and cease() function.
    """

    class ApprovalStatus(models.TextChoices):
        PENDING = "Pending", "Pending"
        APPROVED = "Approved", "Approved"
        REJECTED = "Rejected", "Rejected"

    approval_chain = models.ForeignKey(
        ApprovalChain,
        on_delete=models.PROTECT,
        related_name="txns",
        null=True,
        blank=True,
    )
    approval_status = models.CharField(max_length=20, choices=ApprovalStatus.choices, blank=True)
    approval_status_meta = models.JSONField(default=dict, blank=True)

    class Meta:
        abstract = True

    def get_last_remark(self):
        approval_logs = self.approval_status_meta.get("approval_logs", [])
        rejection_logs = self.approval_status_meta.get("rejection_logs", [])

        if approval_logs:
            return approval_logs[-1].get("remarks")
        if rejection_logs:
            return rejection_logs[-1].get("remarks")
        return None

    @property
    def is_pending(self):
        return self.approval_status == self.ApprovalStatus.PENDING

    def _get_approval_chain(self):
        approval_chains = ApprovalChain.objects.filter(is_obsolete=False, merchant=self.merchant)
        for approval_chain in approval_chains:
            if approval_chain.is_eligible(self):
                self.approval_status = self.ApprovalStatus.PENDING
                return approval_chain

        default_approval_chains = ApprovalChain.objects.filter(is_obsolete=False, merchant__isnull=True)
        for approval_chain in default_approval_chains:
            if approval_chain.is_eligible(self):
                self.approval_status = self.ApprovalStatus.PENDING
                return approval_chain

    @cached_property
    def next_action_and_last_log(self):
        if not self.is_pending:
            return None, None

        app_label = self._meta.app_label
        model = self._meta.model_name
        obj_idx = self.idx

        if ApprovalChainLog.objects.filter(app_label=app_label, model=model, obj_idx=obj_idx).exists():
            last_log = ApprovalChainLog.objects.filter(app_label=app_label, model=model, obj_idx=obj_idx).last()
            return last_log.next_approval_action, last_log

        return self.approval_chain.actions.filter(is_first=True).first(), None

    def _can_approve(self, user):
        next_action, _ = self.next_action_and_last_log
        if not next_action:
            return False

        return next_action.can_take_action(user)

    def approve(self, user, remarks=None):
        if not (user.merchant == self.merchant or user.iss([ROLE.SUPERUSER.value])):
            raise SilkroadException("You are not allowed to take this action.")

        next_action, last_log = self.next_action_and_last_log
        if not next_action:
            raise SilkroadException("This object does not require approval.")

        is_final = next_action.proceed_to_next_action(user, self, remarks, last_log)
        if is_final:
            timestamp = timezone.localtime().strftime("%Y-%m-%d %H:%M:%S")
            self.approval_status = self.ApprovalStatus.APPROVED

            approvals_log = self.approval_status_meta.setdefault("approval_logs", [])
            approval_entry = {
                "approved_by": {
                    "idx": user.idx,
                    "display_name": user.display_name,
                },
                "remarks": remarks,
                "timestamp": timestamp,
            }
            approvals_log.append(approval_entry)

            self.save()
            self.commit(user, remarks)

    def reject(self, user, remarks=None):
        if not self._can_approve(user):
            raise SilkroadException("You are not allowed to take this action.")

        if not self.is_pending:
            raise SilkroadException("This object cannot be rejected.")

        can_resubmit = getattr(self, "can_resubmit_for_approval", False)

        if callable(can_resubmit):
            can_resubmit = can_resubmit()

        if not can_resubmit:
            self.approval_status = self.ApprovalStatus.REJECTED

        timestamp = timezone.localtime().strftime("%Y-%m-%d %H:%M:%S")
        rejections_log = self.approval_status_meta.setdefault("rejection_logs", [])
        rejection_entry = {
            "rejected_by": {
                "idx": user.idx,
                "display_name": user.display_name,
            },
            "remarks": remarks,
            "timestamp": timestamp,
        }
        rejections_log.append(rejection_entry)

        self.save()
        self.cease(user, remarks)

    def commit(self, actor=None, remarks=None):
        raise SilkroadException("The method `commit` must be implemented to use approval chain mixin.")

    def cease(self, actor=None, remarks=None):
        raise SilkroadException("The method `cease` must be implemented to use approval chain mixin.")
