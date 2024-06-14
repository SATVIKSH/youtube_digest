from django.db import models
from django.contrib.auth.models import User
class UserBlogs(models.Model):
    search_query=models.CharField(max_length=1000)
    generated_content = models.TextField()
    created_date = models.DateTimeField(auto_now_add = True)
    links = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE, related_name='user_blogs')
    def __str__(self) -> str:
        return self.search_query

class TranscriptModel(models.Model):
    youtube_link=models.URLField()
    generated_transcript=models.TextField()
    def __str__(self) -> str:
        return self.youtube_link
