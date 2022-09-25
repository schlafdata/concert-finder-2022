from rest_framework import serializers
from .models import Matches

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Matches
        fields = ('Event','Date','Venue','Link','img_url','LikedArtists','song_url')

        
