from django.db import models

# Create your models here.

class Files(models.Model):
    fs_file = models.FileField(upload_to ='uploads/')