from django.db import models
from helpers.models import BaseModel
from django.conf import settings

# Create your models here.
class Role(BaseModel):
    """ Role Model to define different user roles and their permissions. """

    name = models.CharField(max_length=50, unique=True , db_index=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Role"
        verbose_name_plural = "Roles"

    def __str__(self):
        return self.name
