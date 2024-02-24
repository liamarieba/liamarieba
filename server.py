"""Server for Book Club Tracker app."""

from flask import Flask, render_template, request, flash, session, redirect, url_for, jsonify
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
            return redirect(url_for('process_login'))

    return render_template('register.html')

def get_user_club(email):
    user = crud.get_user_by_email(email)

    if user and user.clubs:
        return user.clubs[0]
    else:
        return None


@app.route("/login", methods=["GET", "POST"])
def process_login():
    """Process user login."""
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = crud.get_user_by_email(email)
        if not user or user.password != password:
            flash("The email or password you entered was incorrect.")
            return redirect(url_for('process_login')) 
        else:
            session["user_email"] = user.email

            user_club = get_user_club(email)

            if user_club:
                session["club_id"] = user_club.club_id 
                
            if not user_club:
                flash(f"Welcome back, {user.email}! You are not a member of any club. Please join a club to participate.")
                return redirect(url_for('user_profile', user_id=user.user_id))


            flash(f"Welcome back, {user.email}!")
            return redirect(url_for('user_profile', user_id=user.user_id))

    return render_template("login.html")


@app.route('/user_profile')
def user_profile():
    if 'user_email' not in session:
        return redirect(url_for('process_login'))

    user_email = session['user_email']
    user = crud.get_user_by_email(user_email)
    if not user:
        return redirect(url_for('process_login'))

    clubs = get_user_clubs(user.user_id)
    return render_template('user_profile.html', clubs=clubs) 



@app.route('/clubs')
def clubs():
    clubs = crud.get_all_clubs()
    return render_template('clubs.html', clubs=clubs)

@app.route('/book_club/<int:club_id>')
def book_club_page(club_id):
    if 'user_email' not in session:
        flash("You need to log in to view this page.")
        return redirect(url_for('process_login'))

    club = crud.get_club_by_id(club_id)
    if not club:
        flash("Club not found.")
        return redirect(url_for('show_clubs'))

    current_club_id = session.get('club_id')
    upcoming_meetings = fetch_upcoming_meetings(club_id)  
    books_read = fetch_books_read_by_club(club_id)  

    nominated_books = crud.get_nominated_books_by_club(club_id)
    meetings = club.meetings
    club_members = club.members

    return render_template('book_club.html', club=club, upcoming_meetings=upcoming_meetings, club_members=club_members, books_read=books_read, nominated_books=nominated_books, meetings=meetings, current_club_id=current_club_id)

@app.route('/join/<int:club_id>')
def join_club(club_id):
    if 'user_email' not in session:
        flash("You need to log in to join a club.")
        return redirect(url_for('process_login'))

    user_email = session['user_email']
    user = crud.get_user_by_email(user_email)

    if not user:
        flash("User not found.")
        return redirect(url_for('user_profile'))

    # Check if the user is already a member of any club
    existing_clubs = get_user_clubs(user.user_id)
    if existing_clubs:
        flash("You are already a member of a club and cannot join another.")
        return redirect(url_for('user_profile'))

    club = crud.get_club_by_id(club_id)

    if not club:
        flash("Club not found.")
        return redirect(url_for('show_clubs'))

    # Add user to the club
    club.members.append(user)
    db.session.commit()
    flash("You have successfully joined the club!")

    return redirect(url_for('user_profile'))


def search_books(query, api_key):
    """Search for books using the Google Books API."""
    base_url = "https://www.googleapis.com/books/v1/volumes"
    params = {"q": query, "key": api_key}
    response = requests.get(base_url, params=params)
    return response.json()  


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
        books = results.get('items', [])

        for book in books:
            if not book.get("volumeInfo", {}).get("imageLinks", {}).get("thumbnail"):
               book["volumeInfo"]["imageLinks"] = {"thumbnail": "URL_to_default_image_or_None"}
 
        return render_template('search_results.html', results=books)
    else:
        return render_template('book_search.html')
    

@app.route('/nominate_book', methods=['POST'])
def nominate_book():
    """Nominate a book for voting."""

    if 'user_email' not in session:
        return jsonify({'message': 'You need to log in to nominate a book.'})

    user_email = session['user_email']
    user = crud.get_user_by_email(user_email)

    if not user:
        return jsonify({'message': 'User not found. Please log in again.'})

    data = request.get_json()
    book_id = data.get('book_id')
    client_club_id = data.get('club_id')
    book_details = {
        'title': data.get('title'),
        'author': data.get('author'),
    }

    user_club = next((club for club in user.clubs if club.club_id == client_club_id), None)

    if not user_club:
        return jsonify({'message': 'You are not a member of the specified club.'})

    existing_nomination = NominatedBook.query.filter_by(book_id=book_id, club_id=user_club.club_id).first()

    if existing_nomination:
        return jsonify({'message': 'This book has already been nominated for the club.'})

    nominated_book = crud.nominate_book_for_voting(user_club.club_id, user.user_id, book_id, book_details)

    if nominated_book:
        return jsonify({'message': 'Book nominated successfully'})
    else:
        return jsonify({'message': 'An error occurred during the nomination process.'})


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
    
    nominated_books = crud.get_all_nominated_books()

    return render_template('book_club.html', nominated_books=nominated_books)

@app.route('/vote_date', methods=['POST'])
def vote_for_next_date():
    meeting_id = request.form.get('meeting_id')
    
    user_email = session.get('user_email')
    if not user_email:
        flash("You must log in to vote.")
        return redirect('/login')
    
    user = User.query.filter_by(email=user_email).first()
    if not user:
        flash("User not found.")
        return redirect('/login')
    
    meeting = Meeting.query.get(meeting_id)
    if not meeting:
        flash("Meeting not found.")
        return redirect(url_for('book_club_page'))

    club_id = session.get('club_id')
    existing_vote = NextMeetingDateVote.query.filter_by(user_id=user.user_id, meeting_id=meeting.meeting_id).first()
    if existing_vote:
        flash("You have already voted for a meeting date.")
    else:
        new_vote = NextMeetingDateVote(user_id=user.user_id, meeting_id=meeting.meeting_id)
        db.session.add(new_vote)
        db.session.commit()
        flash("Your vote for the meeting date has been recorded.")

    
    return redirect(url_for('book_club_page', club_id=club_id))


@app.route('/propose_date', methods=['POST'])
def propose_date():
    proposed_date_str = request.form.get('proposed-date')
    user_email = session.get('user_email')
    
    if not user_email:
        flash("You must log in to propose a date.")
        return redirect(url_for('login'))
    
    user = User.query.filter_by(email=user_email).first()
    if not user:
        flash("User not found.")
        return redirect(url_for('login'))

    proposed_date = datetime.strptime(proposed_date_str, '%Y-%m-%d').date()
    
    club_id = session.get('club_id')
    existing_meeting = Meeting.query.filter(Meeting.meeting_date==proposed_date, Meeting.club_id==club_id).first()
    if existing_meeting:
        flash("This date has already been proposed for this club.")
        return redirect(url_for('book_club_page', club_id=club_id))
    
    new_meeting = Meeting(club_id=club_id, meeting_date=proposed_date)
    db.session.add(new_meeting)
    db.session.commit()
    
    flash("Your proposed date has been added.")
    return redirect(url_for('book_club_page', club_id=club_id))



@app.route('/create_club', methods=['GET', 'POST'])
def create_club():
    if request.method == 'POST':
        clubname = request.form['clubname']
        description = request.form['description']
        location = request.form['location']
        
        new_club = Club(clubname=clubname, description=description, location=location)

        db.session.add(new_club)
        db.session.commit()
        
        return redirect(url_for('clubs'))
    else:
        return render_template('create_club.html')

if __name__ == '__main__':
    app.run(debug=True)

 



if __name__ == "__main__":
    connect_to_db(app)
    app.run(host="0.0.0.0", debug=True)