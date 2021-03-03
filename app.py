from operator import imatmul
from flask import Flask, request, render_template, redirect, flash, jsonify, make_response, session, g
from flask_cors import CORS, cross_origin
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from flask_sqlalchemy import SQLAlchemy

import requests

from keys import MAPQUEST_API_KEY
from keys import TRIPOSO_API_KEY
from keys import TRIPOSO_ACCOUNT_KEY


from models import db, connect_db, Saves, User
from forms import UserAddForm, LoginForm

app = Flask(__name__)

CURR_USER_KEY = "curr_user"


app.config['SECRET_KEY'] = "oh-so-secret"
debug = DebugToolbarExtension(app)
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///capstone_project_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)
db.init_app(app)

with app.app_context():
    
    db.create_all()

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id

def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('signup.html', form=form)

@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""
    do_logout()
    return redirect('/login')

@app.route("/")
def home():
    return render_template('main_view.html')

@app.route('/api/<card_id>', methods=["POST"])
def card_updates(card_id):
    if not g.user:
        not_saved = {
            "message": "You need to be signed in to do that"
        }
        return not_saved
    else:
        card_text = request.args['cardText']
        card_title = request.args['cardTitle']
        try:
            card_image = request.args['imageUrl']
            print(card_image)
            card_saved = Saves(id=card_id, name=card_title, snippet=card_text, image_url=card_image)
            db.session.add(card_saved)
            db.session.commit()
        except KeyError:
            card_image = ""
            card_saved = Saves(id=card_id, name=card_title, snippet=card_text)
            db.session.add(card_saved)
            db.session.commit()
            print(card_text)
            print(card_title)
    card_saved = Saves.query.get_or_404(card_id)
    card_send = {
        "imageUrl": card_saved.image_url,
        "cardTitle": card_saved.name,
        "cardText": card_saved.snippet,
        "cardId": card_saved.id
        }

    card_saved = jsonify(card_send)
    return card_saved




@app.route('/api', methods=["POST", "GET"])
def poi_search():

    search_term = request.args['searchTerm']
    search_results = map_quest_q(search_term)
    print(search_results)
    return render_template('poi_box.html', pois=search_results["results"][0]["pois"])

def map_quest_q(location):
    first_poi = location
    response = requests.get('https://www.mapquestapi.com/search/v4/place',
    params={'key': MAPQUEST_API_KEY, 'q': first_poi, 'sort':'relevance'})
    addr = response.json()
    addr = addr["results"][0]["place"]["geometry"]["coordinates"]
    long = addr[0]
    lat = addr[1]
    poi_list = triposo_long_lat(long, lat)
    return poi_list

def triposo_long_lat(long, lat):
    response = requests.get('https://www.triposo.com/api/20201111/local_highlights.json',
    params={'tag_labels':'sightseeing', 'latitude':lat, 'longitude':long, 'max_distance':9999, 
    'token': TRIPOSO_API_KEY, 'account': TRIPOSO_ACCOUNT_KEY})
    poi_list = response.json()
    return poi_list


