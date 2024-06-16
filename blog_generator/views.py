from rest_framework.decorators import api_view,authentication_classes,permission_classes
from rest_framework.authentication import SessionAuthentication,TokenAuthentication
from rest_framework.permissions import IsAuthenticated,AllowAny
from .models import TranscriptModel,UserBlogs
from rest_framework.response import Response
from .serializers import YoutubeSearchSerializer,UserSerializer,UserBlogsSerializer
from rest_framework import status
from django.shortcuts import get_object_or_404
from pytube import YouTube
from django.conf import settings
import os
import json
from bs4 import BeautifulSoup
from markdown import markdown
from groq import Groq
import assemblyai as aai
from googleapiclient.discovery import build 
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from decouple import config
import tempfile
API_KEY = config('API_KEY')

@api_view(['GET'])
def login(request):
    user=get_object_or_404(User,username=request.data['username'])
    if not user.check_password(request.data['password']):
        return Response({"detail":"Not found"},status=status.HTTP_404_NOT_FOUND)
    auth_token,created=Token.objects.get_or_create(user=user)
    serializer=UserSerializer(instance=user)
    return Response({"token":auth_token.key,"username":serializer.data['username'],"email":serializer.data['email']},status=status.HTTP_201_CREATED)


@api_view(['POST'])
def sign_up(request):
    serializer=UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        user=User.objects.get(username=request.data['username'])
        user.set_password(request.data['password'])
        user.save()
        auth_token=Token.objects.create(user=user)
        return Response({"token":auth_token.key,"user":serializer.data},status=status.HTTP_201_CREATED)
    return Response(serializer.error_messages,status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@authentication_classes([SessionAuthentication,TokenAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request):
    return Response(f"passed for {request.user.email}")

@api_view(['POST'])
@authentication_classes([SessionAuthentication,TokenAuthentication])
@permission_classes([IsAuthenticated])
def delete_user(request):
        request.user.delete()
        return Response({"message": "User deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@authentication_classes([SessionAuthentication,TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_user_articles(request):
    articles=UserBlogs.objects.filter(user=request.user)
    serializer=UserBlogsSerializer(articles,many=True)
    return Response(serializer.data)

@api_view(['POST'])
@authentication_classes([SessionAuthentication,TokenAuthentication])
@permission_classes([IsAuthenticated])
def delete_user_article(request):
    blog=UserBlogs.objects.filter(search_query=request.data['search_query'],created_date=request.data['created_date'])
    if blog :
        blog.delete()
        return Response({"message":"Successfully deleted blog"},status=status.HTTP_200_OK)
    else:
        return Response({"error":"Blog article does not exist"},status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@authentication_classes([SessionAuthentication,TokenAuthentication])
@permission_classes([AllowAny])
def process_youtube_search_string(request):
    serializer = YoutubeSearchSerializer(data=request.data)
    if serializer.is_valid():
        search_string = serializer.validated_data['search_string']

        top_videos = get_top_youtube_videos(API_KEY, search_string)
        transcriptions=[]
        titles=[]
        urls=[]
        for title, url in top_videos: 
            if TranscriptModel.objects.filter(youtube_link=url).exists():
                transcription=TranscriptModel.objects.get(youtube_link=url)
                transcriptions.append(transcription.generated_transcript)
            else:
                transcription=get_transcription(url)
                if transcription:
                    transcriptions.append(transcription)
                    transcriptionModel=TranscriptModel(
                        youtube_link=url,
                        generated_transcript=transcription
                    )
                    transcriptionModel.save()
            titles.append(title)
            urls.append(url)

        summary=get_summary(titles,transcriptions)
        if not transcriptions:
            return Response({"error":"Invalid Request method"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if request.user.is_authenticated:
            blog=UserBlogs(
                search_query=search_string,
                generated_content=summary,
                links=json.dumps(urls),
                user=request.user
            )
            blog.save()
        return Response({"title":search_string,"summary": summary, "url": url}, status=status.HTTP_200_OK)
    else:
        return Response({"error":"Invalid Request method"},status=status.HTTP_400_BAD_REQUEST)
    

def yt_title(link):
    yt=YouTube(link)
    title=yt.title
    return title



# def get_transcription(link):
#     yt=YouTube(link)
#     audio=yt.streams.filter(only_audio=True).first()
#     out_file=audio.download(output_path=settings.MEDIA_ROOT,filename="audio.mp3")
#     aai.settings.api_key="5d19f4136c614d01b3622cbdf7df831e"
#     transcriber=aai.Transcriber()
#     transcript=transcriber.transcribe(out_file)
#     os.remove(out_file)
#     return transcript.text

def get_transcription(link):
    try:
        yt = YouTube(link)
        audio = yt.streams.filter(only_audio=True).first()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio_file:
            out_file = audio.download(output_path=os.path.dirname(temp_audio_file.name), filename=os.path.basename(temp_audio_file.name))
        aai.settings.api_key = "5d19f4136c614d01b3622cbdf7df831e"
        
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(out_file)
        
        os.remove(out_file)
        
        return transcript.text
    
    except Exception as e:
        return f"An error occurred: {str(e)}"
    



def get_summary(titles,transcriptions):
    enumerated_transcripts= [f"{i + 1}.{titles[i]}: {query} \n" for i, query in enumerate(transcriptions)]
    client = Groq(
    api_key=config("GROQ_API_KEY"),
    )
    prompt=f"Here is the list of some youtube videos' Transcripts -> \n {enumerated_transcripts}\n .Create an elaborate blog article including points from all the videos. No need to mention the transcripts or videos just make the article. Make sure it is in a human readable form and a little bit informal. Article:"
    response =client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": prompt,
        }
    ],
    model="llama3-8b-8192",
    )
    generated_content= response.choices[0].message.content.strip()
    html = markdown(generated_content)
    text = ''.join(BeautifulSoup(html).findAll(text=True))
    return text


def get_top_youtube_videos(api_key, search_query):
    youtube = build('youtube', 'v3', developerKey=api_key)
    search_response = youtube.search().list(
        q=search_query,
        part='snippet',
        maxResults=5,
        type='video',
        eventType='completed',
        videoDuration='medium',
        videoEmbeddable='true',  
        safeSearch='strict'
    ).execute()
    videos = []
    for item in search_response['items']:
        video_id = item['id']['videoId']
        video_title = item['snippet']['title']
        video_url = f'https://www.youtube.com/watch?v={video_id}'
        videos.append((video_title, video_url))
    
    return videos



