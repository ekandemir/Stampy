from django.db import models

# Create your models here.


class CatalogType(models.Model):

    # Choices Pairs
    # (Saved to database, display name)
    express_id_choices = [(1, 1), (2, 2), (3, 3), (4, 4)]

    name = models.CharField(max_length=255)
    express_id = models.IntegerField(choices=express_id_choices)
    catalog_url = models.CharField(max_length=255)

    def __str__(self):
        return self.name or ''


class SampleCatalog(models.Model):

    # Choices Pairs
    # (Saved to database, display name)
    is_active_choices = [(True, 'Active'), (False, 'Inactive')]

    name = models.CharField(max_length=255)
    is_active = models.BooleanField(choices=is_active_choices)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    catalog_type = models.ForeignKey(CatalogType, on_delete=models.CASCADE)

    def __str__(self):
        return self.name or ''