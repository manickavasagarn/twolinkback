from django.db import models
from django.contrib.auth.models import User

def user_directory_path(instance, filename):
    # file will be uploaded to STATIC_ROOT/userimage/<email>.jpg
    return 'static/userimage/{0}.jpg'.format(instance.user.email)

class UserImage1(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=user_directory_path)  # Add the upload_to parameter
    encoding = models.CharField()
    encoding2 = models.TextField()

    class Meta():
        db_table = "accounts_userimage1"
