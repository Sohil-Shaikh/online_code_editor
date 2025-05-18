from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Project(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name

class File(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    path = models.CharField(max_length=1000)
    is_folder = models.BooleanField(default=False)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class UserSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    active_file = models.ForeignKey(File, null=True, blank=True, on_delete=models.SET_NULL)
    last_activity = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.project.name}"
