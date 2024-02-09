"""Script to seed database."""

import os
import json
from random import choice, randint
from datetime import datetime, timedelta
from server import app
from model import db, connect_to_db, User, Club, Book, UserBookClub, Meeting, NextMeetingDateVote, BookVote, BookClubBook, Review, Rating, NominatedBook
import random

connect_to_db(app)

db.drop_all()
db.create_all()

# Sample data for clubs
clubs = []
for club_index in range(10):
    clubname = f"Club {club_index + 1}"
    description = f"Description for Club {club_index + 1}"
    location = f"Location {club_index + 1}"

    club = Club(clubname=clubname, description=description, location=location)
    db.session.add(club)
    clubs.append(club)

db.session.commit()

# Sample data for users
users = []
for user_index in range(10):
    email = f"user{user_index}@example.com"
    password = "password"

    user = User(email=email, password=password)
    db.session.add(user)
    users.append(user)

db.session.commit()

# Sample data for books
books = []
for book_index in range(10):
    book_id = f"Book-ID-{book_index + 1}"
    title = f"Book {book_index + 1}"
    author = f"Author {book_index + 1}"

    book = Book(book_id=book_id, title=title, author=author)
    db.session.add(book)
    books.append(book)

db.session.commit()

# Create UserBookClub associations
for user in users:
    for _ in range(5):
        club = choice(clubs)
        user_book_club = UserBookClub(user=user, club=club)
        db.session.add(user_book_club)

db.session.commit()

# Seed data for NominatedBook
for club in clubs:
    for _ in range(3):  # Nominating 3 books per club
        user = choice(users)
        book = choice(books)
        votes = randint(0, 10)

        nominated_book = NominatedBook(club=club, user=user, book=book, votes=votes)
        db.session.add(nominated_book)

db.session.commit()

# Insert BookClubBook entries
book_club_books = []
for club in clubs:
    selected_books = random.sample(books, 5)  # Assuming each club has 5 books
    for book in selected_books:
        book_club_book = BookClubBook(club=club, book=book)
        db.session.add(book_club_book)
        book_club_books.append(book_club_book)

db.session.commit()

# Sample data for meetings and related processes
for club in clubs:
    for _ in range(2):  # Assuming 2 meetings per club for simplicity
        meeting_date = datetime.utcnow() + timedelta(days=randint(1, 60))
        meeting = Meeting(club=club, meeting_date=meeting_date)
        db.session.add(meeting)

        # Assuming voting for the next meeting date as an example process
        next_meeting_date = meeting_date + timedelta(days=randint(30, 90))
        for user in random.sample(users, 5):  # Random 5 users vote for the next meeting date
            vote = NextMeetingDateVote(meeting=meeting, user=user, next_meeting_date=next_meeting_date)
            db.session.add(vote)
db.session.commit()

# Sample data for reviews
for book_club_book in book_club_books:
    for _ in range(3):  # Assuming each book_club_book gets 3 reviews
        user = choice(users)
        rating = randint(1, 5)
        comments = f"Random comment for book_club_book {book_club_book.book_club_book_id}"

        review = Review(user=user, book_club_book=book_club_book, rating=rating, comments=comments)
        db.session.add(review)

db.session.commit()
