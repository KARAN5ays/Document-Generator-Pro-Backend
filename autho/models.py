from django.db import models
from helpers.models import BaseModel
from django.core.validators import RegexValidator

class Merchant(BaseModel):
    """ Merchant Model Representing a Business Entity That Can Be Multiple Memo"""
    name = models.CharField(max_length=255 , unique=True , db_index=True)
    description = models.TextField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True , unique=True)
    phone_number = models.CharField(max_length=20, validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$')], blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "autho_merchants"
        verbose_name = "Merchant"
        verbose_name_plural = "Merchants"
        ordering = ['-created_at']

    def __str__(self):
        return self.name