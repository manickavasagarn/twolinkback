from django.db import models
from django.contrib.auth.models import User
from django.db.models import JSONField



def user_directory_path(instance, filename):
    # file will be uploaded to STATIC_ROOT/newuser/<email>.jpg
    return 'static/newuser/{0}.jpg'.format(instance.user.email)

class User_Data(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to=user_directory_path)
    type = models.TextField()
    encoding = models.TextField()

class Test_Info(models.Model):
    test_id = models.TextField(primary_key=True)
    test_title = models.TextField()
    test_desc = models.TextField()
    test_url = models.TextField()

class Test_Questions(models.Model):
    test_id = models.ForeignKey(Test_Info, on_delete=models.CASCADE)
    section_id = models.TextField(primary_key=True)
    section_name = models.TextField()
    section_desc = models.TextField()
    test_questions = JSONField()
    test_answers = JSONField()

class Test_Evaluation(models.Model):
    test_id = models.ForeignKey(Test_Info, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    section_id = models.ForeignKey(Test_Questions, on_delete=models.SET_NULL, null=True)
    answers = JSONField()
    proctoring_score = models.IntegerField()
    test_score = models.IntegerField()