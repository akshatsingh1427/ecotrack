from django.db import models
from django.contrib.auth.models import User
class Organisation(models.Model):
    name=models.CharField(max_length=100,unique=True)
    def __str__(self):return self.name
class Profile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    org=models.ForeignKey(Organisation,null=True,blank=True,on_delete=models.SET_NULL)
    is_admin=models.BooleanField(default=False)
    age=models.PositiveIntegerField();weight=models.FloatField()
    fuel=models.CharField(max_length=10,default='none')
    kmpl=models.FloatField(default=15);vehicle_year=models.PositiveIntegerField(default=2018)
class Activity(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    category=models.CharField(max_length=12);label=models.CharField(max_length=200)
    co2=models.FloatField();avoided=models.FloatField(default=0)
    created=models.DateTimeField(auto_now_add=True)
