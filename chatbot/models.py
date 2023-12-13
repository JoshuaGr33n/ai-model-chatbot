from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser


# Create your models here.


class User(AbstractUser):
    # email = models.EmailField(unique=True)
    phone = models.CharField(max_length=200)

    REQUIRED_FIELDS = ["phone"]
    

class Chat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username}: {self.message}'
    

