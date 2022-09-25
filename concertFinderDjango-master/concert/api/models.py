from django.db import models

# Create your models here.
class Matches(models.Model):
    Event = models.CharField(max_length=255, default = '')
    Date = models.DateTimeField(auto_now=False)
    Venue = models.CharField(max_length=255,default = '')
    Link =  models.CharField(max_length=255,default = '')
    img_url =  models.CharField(max_length=255,default = '')
    LikedArtists = models.CharField(max_length=255,default = '')
    song_url =  models.CharField(max_length=255,default = '')
    # picLink = models.CharField(max_length=255,default = '')

    def __str__(self):
        return self.title
