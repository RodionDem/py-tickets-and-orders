from typing import List, Dict, Optional
from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from db.models import User, Order, Ticket, MovieSession


def create_order(
    tickets: List[Dict[str, int]],
    username: str,
    date: Optional[str] = None
) -> List[Ticket]:

    try:
        user = User.objects.get(username=username)
    except ObjectDoesNotExist:
        raise ValueError(
            f"User with username '{username}' does not exist."
        )

    if date:
        try:
            created_at = datetime.strptime(date, "%Y-%m-%d %H:%M")
        except ValueError:
            raise ValueError("Date must be in format 'YYYY-MM-DD HH:MM'")
    else:
        created_at = datetime.now()

    created_tickets: List[Ticket] = []

    with transaction.atomic():
        order = Order.objects.create(
            user=user,
            created_at=created_at
        )

        for tiket in tickets:
            movie_session = MovieSession.objects.get(id=tiket["movie_session"])

            ticket = Ticket(
                movie_session=movie_session,
                order=order,
                row=tiket["row"],
                seat=tiket["seat"]
            )
            ticket.full_clean()
            ticket.save()
            created_tickets.append(ticket)

    return created_tickets


def get_orders(username: Optional[str] = None) -> List[Ticket]:
    if username:
        user = User.objects.get(username=username)
        return Order.objects.filter(user=user)
    return Order.objects.all()
