from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.
class User(AbstractUser):
    USER_TYPES = (
        ('job_seeker', 'Job Seeker'),
        ('employer', 'Employer'),
        ('admin', 'Admin'),
    )

    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='job_seeker')
    phone_number = PhoneNumberField(blank=True, null=True)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    resume = models.FileField(upload_to='user_resumes/', blank=True, null=True)

    # Additional fields for job seekers
    experience = models.TextField(blank=True)
    education = models.TextField(blank=True)

    # Additional fields for employers
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees'
    )

    def __str__(self):
        return f"{self.username} ({self.user_type})"

    def is_employer(self):
        return self.user_type == 'employer'

    def is_job_seeker(self):
        return self.user_type == 'job_seeker'

    def is_admin_user(self):
        return self.user_type == 'admin' or self.is_staff

