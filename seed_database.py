"""Script to seed database."""

import os
import json
from random import choice, randint
from datetime import datetime, timedelta
from server import app
from model import db, connect_to_db, User, Club, Book, UserBookClub, Meeting, NextMeetingDateVote, BookVote, BookClubBook, Review, Rating, NominatedBook

import crud
import model
import server

connect_to_db(app)

db.drop_all()
db.create_all()

# Sample data for clubs
for club_index in range(10):
    clubname = f"Club {club_index + 1}"
    description = f"Description for Club {club_index + 1}"
    location = f"Location {club_index + 1}"

    club = Club(clubname=clubname, description=description, location=location)
    db.session.add(club)

db.session.commit()

# Sample data for users
for user_index in range(10):
    email = f"user{user_index}@example.com"
    password = "password"

    user = User(email=email, password=password)
    db.session.add(user)

db.session.commit()

# Sample data for books
for book_index in range(10):
    book_id = f"Book-ID-{book_index + 1}" 
    title = f"Book {book_index + 1}"
    author = f"Author {book_index + 1}"
    genre = f"Genre {book_index + 1}"
    published_date = datetime.utcnow() - timedelta(days=randint(1, 365)) 

    book = Book(book_id=book_id, title=title, author=author, genre=genre, published_date=published_date)
    db.session.add(book)

db.session.commit()

actual_book_ids = [book.book_id for book in Book.query.all()]

# Sample data for user-book club associations
for user_index in range(10):
    user = User.query.filter_by(email=f"user{user_index}@example.com").one()
    
    for _ in range(5):
        club_id = randint(1, 10)
        user_book_club = UserBookClub(user_id=user.user_id, club_id=club_id)
        db.session.add(user_book_club)

db.session.commit()

# Seed data for NominatedBook
for club_id in range(1, 11):  
    for _ in range(3):  # Nominating 3 books per club
        user_id = randint(1, 10)  
        book_id = choice(actual_book_ids)
        votes = randint(0, 10)  

        nominated_book = NominatedBook(club_id=club_id, user_id=user_id, book_id=book_id, votes=votes)
        db.session.add(nominated_book)

db.session.commit()

# Sample data for meetings and related
for club_index in range(10):
    club_id = club_index + 1

    for _ in range(2):
        book_id = choice(actual_book_ids)
        meeting_date = datetime.utcnow() + timedelta(days=randint(1, 30))
        voting_deadline = meeting_date - timedelta(days=7)

        meeting = Meeting(club_id=club_id, book_id=book_id, meeting_date=meeting_date, voting_deadline=voting_deadline)
        db.session.add(meeting)
        db.session.flush()

        for _ in range(5):
            user_id = randint(1, 10)
            next_meeting_date_vote = NextMeetingDateVote(meeting_id=meeting.meeting_id, user_id=user_id, next_meeting_date=meeting_date)
            db.session.add(next_meeting_date_vote)

        for _ in range(5):
            user_id = randint(1, 10)
            next_book_id = choice(actual_book_ids)
            book_vote = BookVote(meeting_id=meeting.meeting_id, user_id=user_id, next_book_id=next_book_id)
            db.session.add(book_vote)

        for _ in range(3):
            book_id = choice(actual_book_ids)
            book_club_book = BookClubBook(book_id=book_id, club_id=club_id, meeting_id=meeting.meeting_id, chosen_date=meeting_date)
            db.session.add(book_club_book)

db.session.commit()

# Sample data for reviews
for _ in range(30): # Assuming 30 book club books
    user_id = randint(1, 10)
    book_club_book_id = randint(1, 30)
    rating = randint(1, 5)
    comments = f"Random comment for book club book {book_club_book_id}"

    review = Review


    review = Review(user_id=user_id, book_club_book_id=book_club_book_id, rating=rating, comments=comments)
    db.session.add(review)

db.session.commit()
