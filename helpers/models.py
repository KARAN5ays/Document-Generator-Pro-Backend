from django.db import models
import uuid

# Create your models here.
class BaseModel(models.Model):
    """ Base Model Used Across The Project. provides common fields like id, created_at, updated_at. """

    idx = models.CharField(max_length=20 , unique=True , editable=False , db_index=True)
    is_obsolete = models.BooleanField(default=False, help_text="Soft delete flag. True means the record is obsolete and should not be used.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """ On save, generate a unique idx if not already set. """
        if not self.idx:
            self.idx = uuid.uuid4().hex[:20].upper()  # Generate a unique 20-character ID
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.__class__.__name__} - {self.idx}"