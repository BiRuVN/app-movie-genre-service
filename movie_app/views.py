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
            fields = ['movie_id', 'movie_name', 'duration', 'poster', 'genre_name']
            statement = 'SELECT {}, {}, {}, {}, array_agg({}) \
                    FROM ((movie_app_movie_genre \
                        FULL JOIN movie_app_genre ON movie_app_movie_genre.genre_id_id = movie_app_genre._id) \
                            FULL JOIN movie_app_movie ON movie_app_movie_genre.movie_id_id = movie_app_movie._id) \
                                WHERE movie_app_movie._id IS NOT NULL \
                                    GROUP BY {}, {}, {}, {}'.format("movie_app_movie._id", *fields[1:], *fields[1:-1], "movie_app_movie._id")
                                
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

# Get genre
def get_genre(request):
    if request.method == 'GET':
        fields = ['id', 'genre_name']
        statement = "SELECT * FROM movie_app_genre"

        all_genre = run_sql(statement)        
        data = []
        for genre in all_genre:
            data.append(dict(zip(fields, genre)))
        return JsonResponse({'data' : data})

        # all_genre = serialize(Genre.objects.all(), fields=('_id', 'genre_name'))
        # return JsonResponse({'data' : [x['fields'] for x in all_genre]})

# Create genre
def add_genre(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        try:
            genre = Genre.objects.create(genre_name=body['genre_name'])
        except KeyError:
            return JsonResponse({
                'message': 'Missing key to create genre'
            }, status=status.HTTP_400_BAD_REQUEST)

        return JsonResponse({
            'message': 'Add successfully genre'
        }, status=status.HTTP_201_CREATED)

# Update genre
def update_genre(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        _id = body['id']
        print(_id)
        if _id is None:
            return JsonResponse({
                'message': 'No genre selected'
            }, status=status.HTTP_200_OK)
        
        genre = Genre.objects.get(_id=_id)
        genre.genre_name = body['genre_name']
        genre.save()

        return JsonResponse({
            'message': 'Update genre successfully'
        }, status=status.HTTP_200_OK)

# Create movie_genre
def create_movie_genre(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        try:
            movie_id = body['movie_id']
            genre_id = body['genre_id']
        except KeyError:
            return JsonResponse({
                'message': 'Missing key to create movie_genre'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        movie_genre = Movie_Genre.objects.create(movie_id=movie_id, genre_id=genre_id)

        return JsonResponse({
            'message': 'Add movie_genre successfully'
        }, status=status.HTTP_201_CREATED)
        