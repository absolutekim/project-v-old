
from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    """
    Extended user model.
    Extends the default Django user model to store additional profile information.
    
    This model provides additional fields such as email, nickname, gender, and preferred tags.
    """
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    
    AGE_GROUP_CHOICES = [
        ('under18', 'Under 18'),
        ('18to24', '18-24'),
        ('25to34', '25-34'),
        ('35to44', '35-44'),
        ('45to54', '45-54'),
        ('55to64', '55-64'),
        ('65plus', '65 and Above'),
    ]

    email = models.EmailField(unique=True)  # Email field (required)
    nickname = models.CharField(max_length=30, unique=True, blank=True, null=True)  # User nickname
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)  # Gender (M/F)
    age_group = models.CharField(max_length=10, choices=AGE_GROUP_CHOICES, blank=True, null=True)  # Age group
    selected_tags = models.JSONField(blank=True, null=True)  # User selected tags (3-7 tags)

    def __str__(self):
        return self.username
