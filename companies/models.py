from django.db import models
from users.models import User

# Create your models here.
class Company(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    location = models.CharField(max_length=255, blank=True, null=True)
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    managers = models.ManyToManyField(User, related_name="managed_companies", blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='companies')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

