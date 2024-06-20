from rest_framework import serializers
from .models import UserBlogs
from django.contrib.auth.models import User

class UserBlogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBlogs
        fields = ['search_query','generated_content','created_date','user','links']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields = ['id','username','password','email']

class YoutubeSearchSerializer(serializers.Serializer):
    search_string = serializers.CharField(max_length=1000)

class CheckStatusSerializer(serializers.Serializer):
    task_id = serializers.CharField(max_length=1000)
    



    #AIzaSyDSpDgFUo7hEgtGbCHNxAXMF6_QlbTjPMU