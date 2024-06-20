from rest_framework.decorators import api_view,authentication_classes,permission_classes
from rest_framework.authentication import SessionAuthentication,TokenAuthentication
from rest_framework.permissions import IsAuthenticated,AllowAny
from .models import UserBlogs
from rest_framework.response import Response
from .serializers import YoutubeSearchSerializer,UserSerializer,UserBlogsSerializer,CheckStatusSerializer
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from .tasks import process_youtube_search_string_task
from decouple import config
import json
from celery.result import AsyncResult 
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
        user_id = request.user.id if request.user.is_authenticated else None
        result = process_youtube_search_string_task.delay(API_KEY, search_string, user_id)
        return Response({"task_id": result.id}, status=status.HTTP_202_ACCEPTED)
    else:
        return Response({"error": "Invalid Request"}, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET'])
def check_api_status(request):
    serializer= CheckStatusSerializer(data=request.data)
    if serializer.is_valid():
        task_id=serializer.validated_data['task_id']
        result = AsyncResult(task_id)  
        if result.ready():
           return Response(result.result,status=status.HTTP_200_OK)
        else :
           return Response({'data':'processing'},status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

