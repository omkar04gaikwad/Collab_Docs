from django.db import models

# Create your models here.
class UserProfile(models.Model):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.username