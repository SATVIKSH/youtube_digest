from celery import shared_task
from bs4 import BeautifulSoup
from groq import Groq
import tempfile
import assemblyai as aai
from django.conf import settings
import os
from pytube import YouTube
from markdown import markdown
from decouple import config
from googleapiclient.discovery import build 
from .models import TranscriptModel,UserBlogs
import json


@shared_task
def process_youtube_search_string_task(api_key, search_string, user_id=None):
    top_videos = get_top_youtube_videos(api_key, search_string)
    transcriptions = []
    titles = []
    urls = []

    for title, url in top_videos: 
        if TranscriptModel.objects.filter(youtube_link=url).exists():
            transcription = TranscriptModel.objects.get(youtube_link=url)
            transcriptions.append(transcription.generated_transcript)
        else:
            transcription = get_transcription(url)
            if transcription:
                transcriptions.append(transcription)
                transcriptionModel = TranscriptModel(
                    youtube_link=url,
                    generated_transcript=transcription
                )
                transcriptionModel.save()
        titles.append(title)
        urls.append(url)

    summary = get_summary(titles, transcriptions)
    if user_id:
        User = settings.AUTH_USER_MODEL
        user = User.objects.get(id=user_id)
        blog = UserBlogs(
            search_query=search_string,
            generated_content=summary,
            links=json.dumps(urls),
            user=user
        )
        blog.save()
    return {"title": search_string, "summary": summary, "urls": urls}


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

