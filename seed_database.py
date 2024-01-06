"""Script to seed database."""


import os
import json
from random import choice, randint
from datetime import datetime

import crud
import model
import server


db.drop_all()
db.create_all()

# Sample data for users
for user_index in range(10):
    email = f"user{user_index}@example.com"
    password = "password"

    user = User(email=email, password=password)
    db.session.add(user)

    # Sample data for user-book club associations
    for _ in range(5):
        club_id = randint(1, 10)
        user_book_club = UserBookClub(user_id=user.user_id, club_id=club_id)
        db.session.add(user_book_club)

# Sample data for books
for book_index in range(10):
    title = f"Book {book_index + 1}"
    author = f"Author {book_index + 1}"
    genre = f"Genre {book_index + 1}"
    published_date = datetime.utcnow() - timedelta(days=randint(1, 365))  # Random date within the last year

    book = Book(title=title, author=author, genre=genre, published_date=published_date)
    db.session.add(book)

# Sample data for clubs
for club_index in range(10):
    clubname = f"Club {club_index + 1}"
    description = f"Description for Club {club_index + 1}"
    location = f"Location {club_index + 1}"

    club = Club(clubname=clubname, description=description, location=location)
    db.session.add(club)


db.session.commit()

# Sample data for meetings, next meeting date votes, book votes, book club books, and reviews
for club_index in range(10):
    club_id = club_index + 1

    # Sample data for meetings
    for _ in range(2):
        book_id = randint(1, 10)
        meeting_date = datetime.utcnow() + timedelta(days=randint(1, 30))
        voting_deadline = meeting_date - timedelta(days=7)

        meeting = Meeting(club_id=club_id, book_id=book_id, meeting_date=meeting_date, voting_deadline=voting_deadline)
        db.session.add(meeting)

        # Sample data for next meeting date votes
        for _ in range(5):
            user_id = randint(1, 10)
            next_meeting_date_vote = NextMeetingDateVote(meeting_id=meeting.meeting_id, user_id=user_id, next_meeting_date=meeting_date)
            db.session.add(next_meeting_date_vote)

        # Sample data for book votes
        for _ in range(5):
            user_id = randint(1, 10)
            next_book_id = randint(1, 10)
            book_vote = BookVote(meeting_id=meeting.meeting_id, user_id=user_id, next_book_id=next_book_id)
            db.session.add(book_vote)

        # Sample data for book club books
        for _ in range(3):
            book_id = randint(1, 10)
            chosen_date = meeting_date
            book_club_book = BookClubBook(book_id=book_id, club_id=club_id, meeting_id=meeting.meeting_id, chosen_date=chosen_date)
            db.session.add(book_club_book)

        # Sample data for reviews
        for _ in range(3):
            user_id = randint(1, 10)
            book_club_book_id = randint(1, 30)
            rating = randint(1, 5)
            comments = f"Random comment for book club book {book_club_book_id}"

            review = Review(user_id=user_id, book_club_book_id=book_club_book_id, rating=rating, comments=comments)
            db.session.add(review)


db.session.commit()









