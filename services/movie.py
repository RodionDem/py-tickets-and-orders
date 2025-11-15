from typing import Optional, List
from django.db import models, transaction
from django.db.models import QuerySet

from db.models import Movie


def get_movies(
    genres_ids: Optional[List[int]] = None,
    actors_ids: Optional[List[int]] = None,
    title: Optional[str] = None
) -> QuerySet:

    queryset = Movie.objects.all()

    if title:
        queryset = queryset.filter(title__icontains=title)

    if genres_ids:
        queryset = queryset.filter(genres__id__in=genres_ids)

    if actors_ids:
        queryset = queryset.filter(actors__id__in=actors_ids)

    queryset = queryset.distinct()

    movies_list = list(queryset)

    def sort_key(movie: Movie) -> tuple:
        ticket = movie.title
        if ticket.startswith("Harry Potter"):
            last = ticket.split()[-1]
            if last.isdigit():
                return (0, int(last))
            return (0, 0)
        return (1, ticket.lower())

    movies_list.sort(key=sort_key)

    sorted_ids = [m.id for m in movies_list]

    if not sorted_ids:
        return queryset

    return Movie.objects.filter(id__in=sorted_ids).order_by(
        models.Case(
            *[
                models.When(id=pk, then=pos)
                for pos, pk in enumerate(sorted_ids)
            ]
        )
    )


def get_movie_by_id(movie_id: int) -> Movie:
    return Movie.objects.get(id=movie_id)


def create_movie(
    movie_title: str,
    movie_description: str,
    genres_ids: Optional[List[int]] = None,
    actors_ids: Optional[List[int]] = None
) -> Movie:

    with transaction.atomic():
        movie = Movie.objects.create(
            title=movie_title,
            description=movie_description
        )
        if genres_ids:
            movie.genres.set(genres_ids)
        if actors_ids:
            movie.actors.set(actors_ids)

    return movie
