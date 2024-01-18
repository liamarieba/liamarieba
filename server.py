"""Server for Book Club Tracker app."""

from flask import Flask, render_template, request, flash, session, redirect, url_for
from model import connect_to_db, db, User, UserBookClub, Book, BookVote, Meeting, NextMeetingDateVote, Club, BookClubBook, NominatedBook
from datetime import datetime
import crud
import requests

from jinja2 import StrictUndefined

app = Flask(__name__)
app.secret_key = 'coolestbookclub123'
connect_to_db(app)



# Replace this with routes and view functions!

@app.route('/')
def homepage():
    """View homepage."""

    return render_template('homepage.html')

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    """Register a new user."""
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        user = crud.get_user_by_email(email)
        if user:
            flash("Cannot create an account with that email. Try again.")
        else:
            crud.create_user(email, password) 
            flash("Account created! Please login.")
            return redirect('/login')

    return render_template('register.html')


@app.route("/login", methods=["GET", "POST"])
def process_login():
    """Process user login."""

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = crud.get_user_by_email(email)
        if not user or user.password != password:
            flash("The email or password you entered was incorrect.")
            return redirect("/login") 
        else:
            session["user_email"] = user.email
            flash(f"Welcome back, {user.email}!")

            # Redirect to show_clubs page after successful login
            return redirect(url_for('show_clubs', user_id=user.user_id))

    return render_template("login.html")

@app.route('/show_clubs')
def show_clubs():
    if 'user_email' not in session:
        return redirect(url_for('login'))

    user_email = session['user_email']
    user = crud.get_user_by_email(user_email)
    if not user:
        return redirect(url_for('login'))

    clubs = get_user_clubs(user.user_id)
    return render_template('show_clubs.html', clubs=clubs)


@app.route('/clubs')
def clubs():
    clubs = crud.get_all_clubs()
    return render_template('clubs.html', clubs=clubs)

@app.route('/book_club/<int:club_id>')
def book_club_page(club_id):
    if 'user_email' not in session:
        flash("You need to log in to view this page.")
        return redirect(url_for('login'))

    club = crud.get_club_by_id(club_id)
    if not club:
        flash("Club not found.")
        return redirect(url_for('show_clubs'))

    upcoming_meetings = fetch_upcoming_meetings(club_id)  
    books_read = fetch_books_read_by_club(club_id)  

    nominated_books = club.nominated_books  
    meetings = club.meetings  

    return render_template('book_club.html', club=club, upcoming_meetings=upcoming_meetings, books_read=books_read, nominated_books=nominated_books, meetings=meetings)

@app.route('/join/<int:club_id>')
def join_club(club_id):
    if 'user_email' not in session:
        flash("You need to log in to join a club.")
        return redirect('/login')

    user_email = session['user_email']

    user = crud.get_user_by_email(user_email)

    club = crud.get_club_by_id(club_id)

    if user in club.members:
        flash("You are already a member of this club.")
    else:
        # Add user to the club
        club.members.append(user)
        db.session.commit()
        flash("You have successfully joined the club!")

    return redirect('/show_clubs')

def search_books(query, api_key):
    """Search for books using the Google Books API."""
    base_url = "https://www.googleapis.com/books/v1/volumes"
    params = {"q": query, "key": api_key}
    response = requests.get(base_url, params=params)
    return response.json()  

def nominate_book_for_voting(club_id, user_id, book_id):
    nominated_book = NominatedBook(club_id=club_id, user_id=user_id, book_id=book_id)
    db.session.add(nominated_book)
    db.session.commit()
    return nominated_book

def get_user_clubs(user_id):
    """Return a list of clubs that the user is a member of."""

    user_book_clubs = UserBookClub.query.filter_by(user_id=user_id).all()
    clubs = [ubc.club for ubc in user_book_clubs]
    return clubs

def fetch_upcoming_meetings(club_id):
    """Fetch upcoming meetings for a given club."""
    return Meeting.query.filter(Meeting.club_id == club_id, Meeting.meeting_date >= datetime.now()).all()


def fetch_books_read_by_club(club_id):
    club = Club.query.get(club_id)
    return club.books_read 

@app.route('/book_search', methods=['GET', 'POST'])
def book_search():
    if request.method == 'POST':
        query = request.form.get('query')
        results = search_books(query,'AIzaSyA_Mv9GFDf_BDAeTZjZm_h_rWAjzz0v3Tw') 
        return render_template('search_results.html', results=results.get('items', []))
    else:
        return render_template('book_search.html')
    

@app.route('/nominate_book', methods=['POST'])
def nominate_book():
    """Nominate a book for voting."""

    if 'user_email' not in session:
        flash("You need to log in to nominate a book.")
        return redirect('/login')

    user_email = session['user_email']
    user = crud.get_user_by_email(user_email)

    if not user:
        flash("User not found. Please log in again.")
        return redirect('/login')

    book_id = request.form.get('book_id')
    club_id = request.form.get('club_id')

    existing_nomination = NominatedBook.query.filter_by(book_id=book_id, club_id=club_id).first()

    if existing_nomination:
        flash("This book has already been nominated for the club.")
    else:
        # Create a new nomination record
        nominated_book = NominatedBook(book_id=book_id, club_id=club_id, user_id=user.user_id)
        db.session.add(nominated_book)
        db.session.commit()


    return jsonify({'message': 'Book nominated successfully'})


@app.route('/vote_book', methods=['POST'])
def vote_for_next_book():
    # Retrieve the selected book from the form data
    selected_book_id = request.form.get('book-choice')
    
    user_email = session.get('user_email')
    
    if user_email:
        user = User.query.filter_by(email=user_email).first()
        
        if user:
            selected_book = Book.query.get(selected_book_id)
            if selected_book:
                existing_vote = BookVote.query.filter_by(user_id=user.user_id, meeting_id=selected_book.meeting_id).first()
                
                if existing_vote:
                    flash("You have already voted for a book in this meeting.")
                else:
                    # Create a new BookVote record and save it
                    new_vote = BookVote(user_id=user.user_id, meeting_id=selected_book.meeting_id, next_book_id=selected_book.book_id)
                    db.session.add(new_vote)
                    db.session.commit()
                    
                    flash("Your vote has been recorded.")
            else:
                flash("Invalid book selection.")
        else:
            flash("User not found.")
    else:
        flash("User not authenticated.")
    
    return redirect('/book_club_page')

@app.route('/vote_date', methods=['POST'])
def vote_for_next_date():
    selected_date = request.form.get('meeting-date')
    
    user_email = session.get('user_email')
    
    if user_email:
        user = User.query.filter_by(email=user_email).first()
        
        if user:
            meeting = Meeting.query.filter_by(voting_deadline=selected_date).first()
            
            if meeting:
                existing_vote = NextMeetingDateVote.query.filter_by(user_id=user.user_id, meeting_id=meeting.meeting_id).first()
                
                if existing_vote:
                    flash("You have already voted for a meeting date.")
                else:
                    new_vote = NextMeetingDateVote(user_id=user.user_id, meeting_id=meeting.meeting_id, next_meeting_date=selected_date)
                    db.session.add(new_vote)
                    db.session.commit()
                    
                    flash("Your vote for the meeting date has been recorded.")
            else:
                flash("Invalid meeting date selection.")
        else:
            flash("User not found.")
    else:
        flash("User not authenticated.")
    
    return redirect('/book_club_page')




if __name__ == "__main__":
    connect_to_db(app)
    app.run(host="0.0.0.0", debug=True)

