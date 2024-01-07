"""Server for Book Club Tracker app."""

from flask import Flask, render_template, request, flash, session, redirect
from model import connect_to_db, db
import crud

from jinja2 import StrictUndefined

app = Flask(__name__)
app.secret_key = "dev"
app.jinja_env.undefined = StrictUndefined



# Replace this with routes and view functions!

@app.route('/')
def homepage():
    """View homepage."""

    return render_template('homepage.html')

@app.route("/users", methods=["POST"])
def register_user():
    """Create a new user."""

    email = request.form.get("email")
    password = request.form.get("password")

    user = crud.get_user_by_email(email)
    if user:
        flash("Cannot create an account with that email. Try again.")
    else:
        user = crud.create_user(email, password)
        db.session.add(user)
        db.session.commit()
        flash("Account created! Please log in.")

    return redirect("/")


@app.route("/login", methods=["POST"])
def process_login():
    """Process user login."""

    email = request.form.get("email")
    password = request.form.get("password")

    user = crud.get_user_by_email(email)
    if not user or user.password != password:
        flash("The email or password you entered was incorrect.")
    else:
        # Log in user by storing the user's email in session
        session["user_email"] = user.email
        flash(f"Welcome back, {user.email}!")

    return redirect("/")

def search_books(query, api_key):
    """Search for books using the Google Books API."""
    base_url = "https://www.googleapis.com/books/v1/volumes"
    params = {"q": query, "key": api_key}
    response = requests.get(base_url, params=params)
    return response.json()  

@app.route('/book_search', methods=['GET', 'POST'])
def book_search():
    if request.method == 'POST':
        query = request.form.get('query')
        results = search_books(query, 'AIzaSyA_Mv9GFDf_BDAeTZjZm_h_rWAjzz0v3Tw') 
        return render_template('search_results.html', results=results)
    else:
        return render_template('book_search.html')




if __name__ == "__main__":
    connect_to_db(app)
    app.run(host="0.0.0.0", debug=True)

