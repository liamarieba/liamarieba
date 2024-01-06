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
























