from django.db import models
from django.contrib.auth.models import User
   
class URL(models.Model):
  title = models.CharField(max_length=128, unique=True, default="")
  shorttitle = models.CharField(max_length=28, unique=True, default="")
  cleaned = models.CharField(max_length = 128, default="")
  urltitle = models.CharField(max_length = 128, default="")
  url = models.URLField(unique=True)
  
  def __unicode__(self):
    return self.title

class UserProfile(models.Model):
  user = models.OneToOneField(User)
  website = models.URLField(blank=True)
  recent = models.ManyToManyField(URL)

  def __unicode__(self):
    return self.user.username
  
class CustomComparison(models.Model):
  url1 = models.URLField()
  url2 = models.URLField()
  
  def __unicode__(self):
    return self.url1 + " has been compared to " + self.url2

class URLComparison(models.Model):
  url1 = models.ForeignKey(URL, related_name = "url1")
  url2 = models.ForeignKey(URL, related_name = "url2")
  percent = models.FloatField()
  rating = models.IntegerField(default = 0)
  
  def __unicode__(self):
    return self.url1.url + " is " + str(self.percent) + "% similar to " + self.url2.url
  
class Rating(models.Model):
  urllink = models.ForeignKey(URLComparison, related_name = "urllink")
  user = models.ForeignKey(User)
  updown = models.NullBooleanField()
  
  def __unicode__(self):
    return str(self.user) + " rated something as " + str(self.updown)