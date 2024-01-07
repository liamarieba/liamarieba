"""Models for Book Club Tracker app."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()





class User(db.Model):
    """A user."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)

    ratings = db.relationship("Rating", back_populates="user")

    def __repr__(self):
        return f"<User user_id={self.user_id} email={self.email}>"
    

class UserBookClub(db.Model):
    """Association table for users and book clubs."""

    __tablename__ = "user_book_clubs"

    user_book_club_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    club_id = db.Column(db.Integer, db.ForeignKey("clubs.club_id"), nullable=False)

    user = db.relationship("User", back_populates="user_book_clubs")
    club = db.relationship("Club", back_populates="user_book_clubs")

    def __repr__(self):
        return f"<UserBookClub user_book_club_id={self.user_book_club_id} user_id={self.user_id} club_id={self.club_id}>"


class Club(db.Model):
    """A book club."""

    __tablename__ = "clubs"

    club_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    clubname = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String)

    user_book_clubs = db.relationship("UserBookClub", back_populates="club")
    meetings = db.relationship("Meeting", back_populates="club")
    book_club_books = db.relationship("BookClubBook", back_populates="club")

    def __repr__(self):
        return f"<Club club_id={self.club_id} clubname={self.clubname} location={self.location}>"


class Meeting(db.Model):
    """A book club meeting."""

    __tablename__ = "meetings"

    meeting_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey("clubs.club_id"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("books.book_id"), nullable=False)
    meeting_date = db.Column(db.Date)
    voting_deadline = db.Column(db.Date)

    club = db.relationship("Club", back_populates="meetings")
    book = db.relationship("Book", back_populates="meetings")
    next_meeting_date_votes = db.relationship("NextMeetingDateVote", back_populates="meeting")
    book_votes = db.relationship("BookVote", back_populates="meeting")
    book_club_books = db.relationship("BookClubBook", back_populates="meeting")

    def __repr__(self):
        return f"<Meeting meeting_id={self.meeting_id} club_id={self.club_id} book_id={self.book_id} meeting_date={self.meeting_date} voting_deadline={self.voting_deadline}>"


class NextMeetingDateVote(db.Model):
    """Votes for the next meeting date."""

    __tablename__ = "next_meeting_date_votes"

    next_meeting_date_vote_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    meeting_id = db.Column(db.Integer, db.ForeignKey("meetings.meeting_id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    next_meeting_date = db.Column(db.Date)

    meeting = db.relationship("Meeting", back_populates="next_meeting_date_votes")
    user = db.relationship("User", back_populates="next_meeting_date_votes")

    def __repr__(self):
        return f"<NextMeetingDateVote next_meeting_date_vote_id={self.next_meeting_date_vote_id} meeting_id={self.meeting_id} user_id={self.user_id} next_meeting_date={self.next_meeting_date}>"


class BookVote(db.Model):
    """Votes for the next book."""

    __tablename__ = "book_votes"

    book_vote_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    meeting_id = db.Column(db.Integer, db.ForeignKey("meetings.meeting_id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    next_book_id = db.Column(db.Integer, db.ForeignKey("books.book_id"), nullable=False)

    meeting = db.relationship("Meeting", back_populates="book_votes")
    user = db.relationship("User", back_populates="book_votes")
    next_book = db.relationship("Book", back_populates="book_votes")

    def __repr__(self):
        return f"<BookVote book_vote_id={self.book_vote_id} meeting_id={self.meeting_id} user_id={self.user_id} next_book_id={self.next_book_id}>"


class BookClubBook(db.Model):
    """Books chosen for a book club meeting."""

    __tablename__ = "book_club_books"

    book_club_book_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey("books.book_id"), nullable=False)
    club_id = db.Column(db.Integer, db.ForeignKey("clubs.club_id"), nullable=False)
    meeting_id = db.Column(db.Integer, db.ForeignKey("meetings.meeting_id"), nullable=False)
    chosen_date = db.Column(db.Date)

    book = db.relationship("Book", back_populates="book_club_books")
    club = db.relationship("Club", back_populates="book_club_books")
    meeting = db.relationship("Meeting", back_populates="book_club_books")
    reviews = db.relationship("Review", back_populates="book_club_book")

    def __repr__(self):
        return f"<BookClubBook book_club_book_id={self.book_club_book_id} book_id={self.book_id} club_id={self.club_id} meeting_id={self.meeting_id} chosen_date={self.chosen_date}>"


class Book(db.Model):
    """A book."""

    __tablename__ = "books"

    book_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String, nullable=False)
    author = db.Column(db.String)
    genre = db.Column(db.String)
    published_date = db.Column(db.Date)

    book_club_books = db.relationship("BookClubBook", back_populates="book")
    meetings = db.relationship("Meeting", back_populates="book")
    book_votes = db.relationship("BookVote", back_populates="next_book")

    def __repr__(self):
        return f"<Book book_id={self.book_id} title={self.title} author={self.author} genre={self.genre} published_date={self.published_date}>"


class Review(db.Model):
    """A review of a book in a book club meeting."""

    __tablename__ = "reviews"

    review_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    book_club_book_id = db.Column(db.Integer, db.ForeignKey("book_club_books.book_club_book_id"), nullable=False)
    rating = db.Column(db.Integer)
    comments = db.Column(db.Text)

    user = db.relationship("User", back_populates="reviews")
    book_club_book = db.relationship("BookClubBook", back_populates="reviews")

    def __repr__(self):
        return f"<Review review_id={self.review_id} user_id={self.user_id} book_club_book_id={self.book_club_book_id} rating={self.rating} comments={self.comments}>"


def connect_to_db(app, db_uri='postgresql:///mylocaldb'):
    """Connect the database to Flask app."""
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    from server import app








