from django.db import models

#  Create your models here.
class Movie(models.Model):
    _id = models.AutoField(primary_key=True, null=False)
    movie_name = models.CharField(max_length=50, null=False, unique=True)
    duration = models.IntegerField()
    release_date = models.CharField(max_length=20)
    description = models.TextField(max_length=1024)
    poster = models.CharField(max_length=50)
    trailer = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Genre(models.Model):
    _id = models.AutoField(primary_key=True, null=False)
    genre_name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Movie_Genre(models.Model):
    _id = models.AutoField(primary_key=True, null=False)
    movie_id = models.ForeignKey(Movie, on_delete=models.CASCADE, null=False)
    genre_id = models.ForeignKey(Genre, on_delete=models.CASCADE, null=False)

    class Meta:
        unique_together = ['movie_id', 'genre_id']
