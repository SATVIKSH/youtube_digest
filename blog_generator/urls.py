from django.urls import path
from . import views

urlpatterns=[
    path('signup/',views.sign_up,name='sign_up'),
     path('login/',views.login,name='login'),
     path('delete-user/',views.delete_user,name='delete-user'),
      path('get-articles/',views.get_user_articles,name='get-articles'),
         path('delete-article/',views.delete_user_article,name='delete-article'),
      path('test-token/',views.test_token,name='test_token'),
    path('youtube-search/',views.process_youtube_search_string,name='youtube-search')
]