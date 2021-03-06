from django.http import JsonResponse
from rest_framework import status
from movie_app.models import *
from django.core import serializers
import rest_framework
import ast
import json
from django.db import connection
import requests
import base64

def check_token(token):
    token = token.split(' ')[1]
    payload = token.split('.')[1]
    payload += "=" * ((4 - len(payload) % 4) % 4)
    payload_byte = base64.b64decode(payload)
    x = ''.join(map(chr, list(payload_byte)))
    
    auth = {}
    for role in ['ROLE_EMPLOYEE', 'ROLE_GUEST', 'ROLE_ADMIN']:
        if role in x:
            auth['ROLE'] = role
            break
    for action in ['MOVIE.READ', 'MOVIE.UPDATE', 'MOVIE.CREATE', 
                    'GENRE.CREATE', 'GENRE.READ', 'GENRE.UPDATE']:
        auth[action] = True if action in x else False

    return auth

def run_sql(statement):
    with connection.cursor() as cursor:
        cursor.execute(statement)
        if statement.startswith('SELECT'):
            row = cursor.fetchall()
            return row
        cursor.commit()

# Create your views here.
# Get all movies
def get_movie(request):
    if request.method == 'GET':
        _id = request.GET.get('id', None)
        fields = []
        statement = []
        try:
            auth = check_token(request.headers['authorization'])
            if (auth['ROLE'] == 'ROLE_EMPLOYEE' or auth['ROLE'] == 'ROLE_ADMIN'):
                pass

            if _id is None:
                fields = ['movie_id', 'movie_name', 'duration', 'poster', 'release_date', 'status', 'genre_name']
                statement = 'SELECT {}, {}, {}, {}, {}, {}, array_agg({}) \
                        FROM ((movie_app_movie_genre \
                            FULL JOIN movie_app_genre ON movie_app_movie_genre.genre_id_id = movie_app_genre._id) \
                                FULL JOIN movie_app_movie ON movie_app_movie_genre.movie_id_id = movie_app_movie._id) \
                                    WHERE movie_app_movie._id IS NOT NULL \
                                        GROUP BY {}, {}, {}, {}, {}, {}'.format("movie_app_movie._id", *fields[1:], *fields[1:-1], "movie_app_movie._id")
            else:
                fields = ['movie_id', 'movie_name', 'duration', 'poster', 'release_date', 'trailer', 'description', 'status', 'genre_name']
                statement = 'SELECT {}, {}, {}, {}, {}, {}, {}, {}, array_agg({}) \
                        FROM ((movie_app_movie_genre \
                            FULL JOIN movie_app_genre ON movie_app_movie_genre.genre_id_id = movie_app_genre._id) \
                                FULL JOIN movie_app_movie ON movie_app_movie_genre.movie_id_id = movie_app_movie._id) \
                                    WHERE movie_app_movie._id={} \
                                    GROUP BY {}, {}, {}, {}, {}, {}, {}, {}'.format("movie_app_movie._id", *fields[1:], str(_id), *fields[1:-1], "movie_app_movie._id")
        except:
            if _id is None:
                fields = ['movie_id', 'movie_name', 'duration', 'poster', 'release_date', 'status', 'genre_name']
                statement = 'SELECT {}, {}, {}, {}, {}, {}, array_agg({}) \
                        FROM ((movie_app_movie_genre \
                            FULL JOIN movie_app_genre ON movie_app_movie_genre.genre_id_id = movie_app_genre._id) \
                                FULL JOIN movie_app_movie ON movie_app_movie_genre.movie_id_id = movie_app_movie._id) \
                                    WHERE movie_app_movie._id IS NOT NULL AND movie_app_movie.status != 1 \
                                        GROUP BY {}, {}, {}, {}, {}, {}'.format("movie_app_movie._id", *fields[1:], *fields[1:-1], "movie_app_movie._id")
            else:
                fields = ['movie_id', 'movie_name', 'duration', 'poster', 'release_date', 'trailer', 'description', 'status', 'genre_name']
                statement = 'SELECT {}, {}, {}, {}, {}, {}, {}, {}, array_agg({}) \
                        FROM ((movie_app_movie_genre \
                            FULL JOIN movie_app_genre ON movie_app_movie_genre.genre_id_id = movie_app_genre._id) \
                                FULL JOIN movie_app_movie ON movie_app_movie_genre.movie_id_id = movie_app_movie._id) \
                                    WHERE movie_app_movie._id={} AND movie_app_movie.status != 1 \
                                    GROUP BY {}, {}, {}, {}, {}, {}, {}, {}'.format("movie_app_movie._id", *fields[1:], str(_id), *fields[1:-1], "movie_app_movie._id")
        
        all_movies = run_sql(statement)
   
        data = []
        for movie in all_movies:
            data.append(dict(zip(fields, movie)))

        return JsonResponse({'data' : data}, status=status.HTTP_200_OK)

# Create movie
def add_movie(request):
    if request.method == 'POST':
        try:
            auth = check_token(request.headers['authorization'])
        except:
            return JsonResponse({
                'message': 'Mising auth token'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not (auth['ROLE'] == 'ROLE_EMPLOYEE' or auth['ROLE'] == 'ROLE_ADMIN'):
            return JsonResponse({
                'message': 'Permission denied'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not auth['MOVIE.CREATE']:
            return JsonResponse({
                'message': 'CREATE permission denied'
            }, status=status.HTTP_400_BAD_REQUEST)

        body = json.loads(request.body)
        genres = body['genre_ids']
        try:
            movie = Movie.objects.create(
                movie_name=body['movie_name'], duration=body['duration'], poster=body['poster'],
                release_date=body['release_date'], trailer=body['trailer'], description=body['description'],
                status=body['movie_status']
                )
        except KeyError:
            return JsonResponse({
                'message': 'Missing key to create'
            }, status=status.HTTP_400_BAD_REQUEST)
        except:
            return JsonResponse({
                'message': 'Duplicated records'
            }, status=status.HTTP_400_BAD_REQUEST)

        if movie is None:
            return JsonResponse({
                'message': 'Add movie unsuccessfully'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            for genre_id in genres:
                Movie_Genre.objects.create(movie_id=Movie(_id=movie._id), genre_id=Genre(_id=genre_id))
        except:
            return JsonResponse({
                'message': 'Problem occurred when add genre to movie'
            }, status=status.HTTP_400_BAD_REQUEST)

        return JsonResponse({
            'message': 'Add movie successfully'
        }, status=status.HTTP_201_CREATED)

# Delete movie
# def del_movie(request):
#     if request.method == 'POST':
#         body = json.loads(request.body)
#         _id = body['id']
#         print(_id)
#         if _id is None:
#             return JsonResponse({
#                 'message': 'No movie deleted'
#             }, status=status.HTTP_400_BAD_REQUEST)
        
#         del_status = Movie.objects.filter(_id=_id).delete()
#         # print(del_status)
#         try:
#             return JsonResponse({
#                 'message': '{} movie deleted'.format(del_status[1]['movie_app.Movie'])
#             }, status=status.HTTP_200_OK)
#         except KeyError:
#              return JsonResponse({
#                 'message': 'No movie available to be deleted'
#             }, status=status.HTTP_400_BAD_REQUEST)

# Update movie
def update_movie(request):
    if request.method == 'POST':
        try:
            auth = check_token(request.headers['authorization'])
        except:
            return JsonResponse({
                'message': 'Mising auth token'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not (auth['ROLE'] == 'ROLE_EMPLOYEE' or auth['ROLE'] == 'ROLE_ADMIN'):
            return JsonResponse({
                'message': 'Permission denied'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not auth['MOVIE.UPDATE']:
            return JsonResponse({
                'message': 'UPDATE permission denied'
            }, status=status.HTTP_400_BAD_REQUEST)

        body = json.loads(request.body)
        _id = body['id']
        genres = body['genre_ids']
        if _id is None:
            return JsonResponse({
                'message': 'No movie selected'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            movie = Movie.objects.get(_id=_id)
        except:
            return JsonResponse({
                'message': 'No available movie to be updated'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            movie.movie_name = body['movie_name']
            movie.duration = body['duration']
            movie.poster = body['poster']
            movie.description = body['description']
            movie.trailer = body['trailer']
            movie.release_date = body['release_date']
            movie.status = body['movie_status']
            movie.save()
            
            try:
                Movie_Genre.objects.filter(movie_id=_id).delete()
            except:
                return JsonResponse({
                    'message': 'Problems occurred when delete old genres of movie'
                }, status=status.HTTP_400_BAD_REQUEST)

            try:
                for genre_id in genres:
                    Movie_Genre.objects.create(movie_id=Movie(_id=_id), genre_id=Genre(_id=genre_id))
            except:
                return JsonResponse({
                    'message': 'Problem occurred when add genre to movie'
                }, status=status.HTTP_400_BAD_REQUEST)

            return JsonResponse({
                'message': 'Update movie successfully'
            }, status=status.HTTP_200_OK)
        except:
            return JsonResponse({
                'message': 'Just exception'
            }, status=status.HTTP_400_BAD_REQUEST)

# Get genre
def get_genre(request):
    if request.method == 'GET':
        fields = ['id', 'genre_name']
        statement = "SELECT _id, genre_name FROM movie_app_genre"

        all_genre = run_sql(statement)        
        data = []
        for genre in all_genre:
            data.append(dict(zip(fields, genre)))
        return JsonResponse({'data' : data}, status=status.HTTP_200_OK)

# Create genre
def add_genre(request):
    if request.method == 'POST':
        try:
            auth = check_token(request.headers['authorization'])
        except:
            return JsonResponse({
                'message': 'Mising auth token'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not (auth['ROLE'] == 'ROLE_EMPLOYEE' or auth['ROLE'] == 'ROLE_ADMIN'):
            return JsonResponse({
                'message': 'Permission denied'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not auth['GENRE.CREATE']:
            return JsonResponse({
                'message': 'CREATE permission denied'
            }, status=status.HTTP_400_BAD_REQUEST)

        body = json.loads(request.body)
        try:
            genre = Genre.objects.create(genre_name=body['genre_name'])
        except KeyError:
            return JsonResponse({
                'message': 'Missing key to create genre'
            }, status=status.HTTP_400_BAD_REQUEST)
        except:
            return JsonResponse({
                'message': 'Duplicate genre name in database'
            }, status=status.HTTP_400_BAD_REQUEST)

        return JsonResponse({
            'data': {
                'id': genre._id,
                'genre_name': genre.genre_name
            }
        }, status=status.HTTP_201_CREATED)

# Update genre
def update_genre(request):
    if request.method == 'POST':
        try:
            auth = check_token(request.headers['authorization'])
        except:
            return JsonResponse({
                'message': 'Mising auth token'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not (auth['ROLE'] == 'ROLE_EMPLOYEE' or auth['ROLE'] == 'ROLE_ADMIN'):
            return JsonResponse({
                'message': 'Permission denied'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not auth['GENRE.UPDATE']:
            return JsonResponse({
                'message': 'UPDATE permission denied'
            }, status=status.HTTP_400_BAD_REQUEST)

        body = json.loads(request.body)
        _id = body['id']
        print(_id)
        if _id is None:
            return JsonResponse({
                'message': 'No genre selected'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            genre = Genre.objects.get(_id=_id)
            genre.genre_name = body['genre_name']
            genre.save()
        except:
            return JsonResponse({
                'message': 'Duplicate genre name in database'
            }, status=status.HTTP_400_BAD_REQUEST)

        return JsonResponse({
            'message': 'Update genre successfully'
        }, status=status.HTTP_200_OK)
