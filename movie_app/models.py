from django.db import models

#  Create your models here.
class Movie(models.Model):
    class MovieStatus(models.IntegerChoices):
        NOT_SHOW = 1, "NOT_SHOW"
        IS_SHOWING = 2, "IS_SHOWING"
        WILL_SHOW = 3, "WILL_SHOW"

    _id = models.AutoField(primary_key=True, null=False)
    movie_name = models.CharField(max_length=50, null=False, unique=True)
    duration = models.IntegerField()
    release_date = models.CharField(max_length=20)
    description = models.TextField(max_length=1024)
    poster = models.TextField(max_length=50)
    trailer = models.TextField(max_length=50)
    status = models.IntegerField(
        choices=MovieStatus.choices,
        default=MovieStatus.WILL_SHOW
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Genre(models.Model):
    _id = models.AutoField(primary_key=True, null=False)
    genre_name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Movie_Genre(models.Model):
    _id = models.AutoField(primary_key=True, null=False)
    movie_id = models.ForeignKey(Movie, on_delete=models.CASCADE, null=False)
    genre_id = models.ForeignKey(Genre, on_delete=models.CASCADE, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['movie_id', 'genre_id']
