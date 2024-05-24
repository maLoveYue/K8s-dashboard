from django.db import models

# Create your models here.

class User(models.Model):
    token = models.CharField(max_length=50)
    auth_type = models.CharField(max_length=30)
    content = models.TextField()
    datetime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.token

    class Meta:
        db_table = 'user'
