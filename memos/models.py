from django.db import models
from approvals.models import ApprovalChainMixin
from helpers.models import BaseModel
from django.conf import settings
from django.core.validators import MinValueValidator
import uuid
import logging

logger = logging.getLogger(__name__)
# Create your models here.
class Memo(ApprovalChainMixin, BaseModel):
    """ Memo Model representing a document that goes through an approval process. """
    class Types(models.TextChoices):
        GENERAL = 'GENERAL', 'General'
        FINANCE = 'FINANCE', 'Finance'
        HR = 'HR', 'Human Resources'
        IT = 'IT', 'Information Technology'
        OTHER = 'OTHER', 'Other'
    merchant= models.ForeignKey('autho.Merchant', on_delete=models.PROTECT, related_name='memos')
    title = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2 , validators=[MinValueValidator(0.01)]) 
    from_department = models.CharField(max_length=100)
    to_department = models.CharField(max_length=100)
    subject = models.CharField(max_length=255)
    purpose = models.TextField()
    background = models.TextField()
    memo_type = models.CharField(max_length=20, choices=Types.choices , default=Types.GENERAL)
    reference_number = models.CharField(max_length=100, unique=True , db_index=True ,editable=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='created_memos')

    class Meta:
        verbose_name = "Memo"
        verbose_name_plural = "Memos"

    @staticmethod
    def generate_reference_number():
        """ Generate a unique reference number for the memo. """
        return f"MEMO-{uuid.uuid4().hex[:8].upper()}"
    

    def save(self, *args, **kwargs):
        """ Override save to generate reference number if not set. """
        if not self.reference_number:
            while True:
                ref = self.generate_reference_number()
                if not Memo.objects.filter(reference_number=ref).exists():
                    self.reference_number = ref
                    break
        super().save(*args, **kwargs)
    

    def commit(self, actor=None, remarks=None):
        """ This hook is called when the memo is FINALLY APPROVED by the last approver. """
        logger.info(f"[Approved] Memo {self.idx} approved by {actor} with remarks: {remarks}")

    def cease(self, actor=None, remarks=None):
        """ This hook is called when the memo is REJECTED. """
        logger.warning(f"[Rejected] Memo {self.idx} rejected by {actor} with remarks: {remarks}")