from django.urls import path
from .views import *
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    # path('', ),
    path('movie/', get_movie),
    path('movie/new', csrf_exempt(add_movie)),
    path('movie/del', csrf_exempt(del_movie)),
    path('movie/update', csrf_exempt(update_movie)),

    path('gerne/', get_gerne),
    path('gerne/new', csrf_exempt(add_gerne)),
    path('gerne/update', csrf_exempt(update_gerne)),
    path('movie_gerne/add', csrf_exempt(create_movie_gerne))
    
]
