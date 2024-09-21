# Youtube Digest
A RESTful service designed to extract insightful data from YouTube videos.
With just a YouTube video link as input, this API delivers multiple capabilities to help users better understand video content and audience sentiment.
It is a powerful tool for content creators, marketers, and researchers looking to quickly gather actionable insights from YouTube videos and their engagement metrics.


## Key Features
### Video Content Blogging
The API analyzes the content of the video and generates a concise blog article summarizing its main points. This allows users to quickly grasp the video's topic without watching it in full.

### Comment Sentiment Analysis
The API also performs sentiment analysis on the comments section of the video. It categorizes comments into three types:
  - Positive: Comments expressing appreciation or favorable opinions about the video.
  - Negative: Comments that reflect criticism or dissatisfaction.
  - Neutral: Comments that neither praise nor criticize but offer objective observations or questions.

### Comment Summary
In addition to categorizing the comments, the API provides an aggregated summary of the overall sentiment, helping users understand the general perception of the video by its audience.

## Workflow
### Video Content Blogging
![Black White Minimalist Boho Grid Background Page Border A4 (Landscape)](https://github.com/user-attachments/assets/1581573d-d32b-41c5-90af-09927a8bb556)

### Sentimental Analysis on Comments
![Copy of Black White Minimalist Boho Grid Background Page Border A4 (Landscape)](https://github.com/user-attachments/assets/e473bb79-6d6e-4bda-ae82-cb3a707c78e2)



## About the project
The API is built using Django Rest Framework and leverages multiple external services to accomplish the tasks described above.
### Key External APIs and Libraries
#### YouTube Data API (googleapiclient.discovery.build)
  - Used to extract video details (e.g., title, description, and comments) and to fetch captions if available.
  - Retrieves up to 600 top-level comments for sentiment analysis.
#### AssemblyAI
  - A transcription service that processes audio extracted from videos to generate accurate transcripts.

#### MoviePy (moviepy.editor.VideoFileClip)
  - Extracts audio from downloaded YouTube videos for transcription purposes.

#### VaderSentiment (vaderSentiment.vaderSentiment.SentimentIntensityAnalyzer)
  - Conducts sentiment analysis on YouTube comments, categorizing them as positive, negative, or neutral.
#### Groq
  - An AI service for generating the blog article and summarizing the comments by processing video transcriptions and comment sentiment analysis results.
#### BeautifulSoup (bs4)
  - Cleans up the generated content (e.g., blog or comments summary) by removing any unnecessary HTML formatting.

## Main Functions
#### get_result(url, title):
  - Main task that ties all processes together, generating the video transcription, summarizing the transcription into a blog article, performing sentiment analysis on comments, and summarizing the categorized comments.
#### generate_transcription(video_url, use_whisper):
  - Downloads the video, extracts the audio, and uses AssembyAI to transcribe the audio into text.
#### get_sentiment_analysis(link):
  - Retrieves YouTube comments, filters out irrelevant ones, and performs sentiment analysis using VaderSentiment, categorizing them as positive, negative, or neutral.
#### summarize_comments(positive_comments, negative_comments, neutral_comments):
  - Summarizes the comments into a general consensus using Groq’s AI service.
#### get_summary(title, transcription):
  - Uses Groq to generate a concise blog article summarizing the transcription of the video.

