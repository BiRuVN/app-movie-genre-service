from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import status
from movie_app.models import *
from django.core import serializers
import rest_framework
import ast
import json
from django.db import connection

def run_sql(statement):
    with connection.cursor() as cursor:
        cursor.execute(statement)
        if statement.startswith('SELECT'):
            row = cursor.fetchall()
            return row
        cursor.commit()

def serialize(querysetObject, fields=()):
    return ast.literal_eval(serializers.serialize('json', querysetObject, fields=fields))

# Create your views here.

# Get all movies
def get_movie(request):
    if request.method == 'GET':
        _id = request.GET.get('id', None)

        fields = []
        statement = []
        if _id is None:
            fields = ['movie_name', 'duration', 'poster', 'genre_name']
            statement = 'SELECT {}, {}, {}, array_agg({}) \
                    FROM ((movie_app_movie_genre \
                        FULL JOIN movie_app_genre ON movie_app_movie_genre.genre_id_id = movie_app_genre._id) \
                            FULL JOIN movie_app_movie ON movie_app_movie_genre.movie_id_id = movie_app_movie._id) \
                                GROUP BY {}, {}, {}'.format(*fields, *fields[:-1])
                                
        else:
            fields = ['movie_name', 'duration', 'poster', 'release_date', 'trailer', 'description', 'genre_name']
            statement = 'SELECT {}, {}, {}, {}, {}, {}, array_agg({}) \
                    FROM ((movie_app_movie_genre \
                        FULL JOIN movie_app_genre ON movie_app_movie_genre.genre_id_id = movie_app_genre._id) \
                            FULL JOIN movie_app_movie ON movie_app_movie_genre.movie_id_id = movie_app_movie._id) \
                                WHERE movie_app_movie._id={} \
                                GROUP BY {}, {}, {}, {}, {}, {}'.format(*fields, str(_id), *fields[:-1])

        all_movies = run_sql(statement)        
        data = []
        for movie in all_movies:
            data.append(dict(zip(fields, movie)))
        return JsonResponse({'data' : data})
        
# Create movie
def add_movie(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        try:
            movie = Movie.objects.create(
                movie_name=body['movie_name'], duration=body['duration'], poster=body['poster'],
                release_date=body['release_date'], trailer=body['trailer'], description=body['description']
                )
        except KeyError:
            return JsonResponse({
                'message': 'Missing key to create'
            }, status=status.HTTP_400_BAD_REQUEST)

        if movie is None:
            return JsonResponse({
                'message': 'Add movie unsuccessfully'
            }, status=status.HTTP_400_BAD_REQUEST)

        return JsonResponse({
            'message': 'Add movie successfully'
        }, status=status.HTTP_201_CREATED)

# Delete movie
def del_movie(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        _id = body['id']
        print(_id)
        if _id is None:
            return JsonResponse({
                'message': 'No movie deleted'
            }, status=status.HTTP_200_OK)
        
        del_status = Movie.objects.filter(_id=_id).delete()
        # print(del_status)
        try:
            return JsonResponse({
                'message': '{} movie deleted'.format(del_status[1]['movie_app.Movie'])
            }, status=status.HTTP_200_OK)
        except KeyError:
             return JsonResponse({
                'message': 'No movie available to be deleted'
            }, status=status.HTTP_200_OK)

# Update movie
def update_movie(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        _id = body['id']
        # print(_id)
        if _id is None:
            return JsonResponse({
                'message': 'No movie selected'
            }, status=status.HTTP_200_OK)
        
        try:
            movie = Movie.objects.get(_id=_id)
        except:
            return JsonResponse({
                'message': 'No available movie to be updated'
            }, status=status.HTTP_200_OK)

        movie.movie_name = body['movie_name']
        movie.duration = body['duration']
        movie.poster = body['poster']
        movie.description = body['description']
        movie.trailer = body['trailer']
        movie.release_date = body['release_date']
        movie.save()

        return JsonResponse({
            'message': 'Update movie successfully'
        }, status=status.HTTP_200_OK)

# Get gerne
def get_genre(request):
    if request.method == 'GET':
        all_gerne = serialize(Gerne.objects.all(), fields=('genre_name'))
        return JsonResponse({'data' : [x['fields'] for x in all_gerne]})

# Create gerne
def add_genre(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        try:
            gerne = Gerne.objects.create(genre_name=body['genre_name'])
        except KeyError:
            return JsonResponse({
                'message': 'Missing key to create gerne'
            }, status=status.HTTP_400_BAD_REQUEST)

        return JsonResponse({
            'message': 'Add successfully gerne'
        }, status=status.HTTP_201_CREATED)

# Update gerne
def update_genre(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        _id = body['id']
        print(_id)
        if _id is None:
            return JsonResponse({
                'message': 'No gerne selected'
            }, status=status.HTTP_200_OK)
        
        gerne = Gerne.objects.get(_id=_id)
        gerne.genre_name = body['genre_name']
        gerne.save()

        return JsonResponse({
            'message': 'Update gerne successfully'
        }, status=status.HTTP_200_OK)

# Create movie_gerne
def create_movie_genre(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        try:
            movie_id = body['movie_id']
            gerne_id = body['gerne_id']
        except KeyError:
            return JsonResponse({
                'message': 'Missing key to create movie_gerne'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        movie_gerne = Movie_Gerne.objects.create(movie_id=movie_id, gerne_id=gerne_id)

        return JsonResponse({
            'message': 'Add movie_gerne successfully'
        }, status=status.HTTP_201_CREATED)
        