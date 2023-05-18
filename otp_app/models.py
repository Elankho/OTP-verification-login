from django.db import models


class User(models.Model):
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=6)
    otp_timestamp = models.DateTimeField()
    wrong_attempts = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.email
