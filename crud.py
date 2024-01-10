"""CRUD operations."""


from model import db, User, Club, Meeting, Book, Review


def create_user(email, password):
    """Create a new user."""
    user = User(email=email, password=password)
    db.session.add(user)
    db.session.commit()
    return user


def get_user_by_id(user_id):
    """Retrieve a user by user_id."""
    return User.query.get(user_id)





def create_club(clubname, description, location):
    club = Club(clubname=clubname, description=description, location=location)
    db.session.add(club)
    db.session.commit()
    return club


def create_meeting(club_id, book_id, meeting_date, voting_deadline):
    meeting = Meeting(club_id=club_id, book_id=book_id, meeting_date=meeting_date, voting_deadline=voting_deadline)
    db.session.add(meeting)
    db.session.commit()
    return meeting

def get_meeting_by_id(meeting_id):
    return Meeting.query.get(meeting_id)

def update_meeting(meeting_id, new_book_id, new_meeting_date, new_voting_deadline):
    meeting = get_meeting_by_id(meeting_id)
    meeting.book_id = new_book_id
    meeting.meeting_date = new_meeting_date
    meeting.voting_deadline = new_voting_deadline
    db.session.commit()

def delete_meeting(meeting_id):
    meeting = get_meeting_by_id(meeting_id)
    db.session.delete(meeting)
    db.session.commit()

# Update meeting attributes (e.g., book_id, meeting_date, voting_deadline)
def update_meeting(meeting_id, new_book_id, new_meeting_date, new_voting_deadline):
    meeting = get_meeting_by_id(meeting_id)
    meeting.book_id = new_book_id
    meeting.meeting_date = new_meeting_date
    meeting.voting_deadline = new_voting_deadline
    db.session.commit()

def get_meetings_by_club(club_id):
    return Meeting.query.filter_by(club_id=club_id).all()

def create_book(title, author, genre, published_date):
    book = Book(title=title, author=author, genre=genre, published_date=published_date)
    db.session.add(book)
    db.session.commit()
    return book

def get_book_by_id(book_id):
    return Book.query.get(book_id)

def get_all_books():
    return Book.query.all()

def delete_book(book_id):
    book = get_book_by_id(book_id)
    db.session.delete(book)
    db.session.commit()


def create_review(user_id, book_club_book_id, rating, comments):
    review = Review(user_id=user_id, book_club_book_id=book_club_book_id, rating=rating, comments=comments)
    db.session.add(review)
    db.session.commit()
    return review


def get_reviews_by_book_club_book(book_club_book_id):
    return Review.query.filter_by(book_club_book_id=book_club_book_id).all()

#update reviews
def update_review(review_id, new_rating, new_comments):
    review = get_review_by_id(review_id)
    review.rating = new_rating
    review.comments = new_comments
    db.session.commit()





if __name__ == '__main__':
    from server import app
    connect_to_db(app)





