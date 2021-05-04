from django.urls import path
from .views import *
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    # path('', ),
    path('movie/', get_movie),
    path('movie/new', csrf_exempt(add_movie)),
    path('movie/del', csrf_exempt(del_movie)),
    path('movie/update', csrf_exempt(update_movie)),

    path('genre/', get_genre),
    path('genre/new', csrf_exempt(add_genre)),
    path('genre/update', csrf_exempt(update_genre)),
    path('movie_genre/add', csrf_exempt(create_movie_genre))
    
]
