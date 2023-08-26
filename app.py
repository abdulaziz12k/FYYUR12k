import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
from sqlalchemy import func
from flask_wtf import CSRFProtect
# protect against Cross-Site Request Forgery (CSRF) attacks
# When the user submits the form or clicks on the URL, the token is sent along with the request. The server-side application then
# verifies that the token is valid and matches the one associated with the user’s session before processing the request
from models import *

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#
app = Flask(__name__)
# called out in every form sent throught html files that has POST method used #
csrf = CSRFProtect(app)
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql://postgres:azoozyh1122@localhost:5432/project"
db = SQLAlchemy(app)
session = db.session
migrate = Migrate(app, db)
moment = Moment(app)
app.config.from_object("config")
# ----------------------------------------------------------------------------#
# Models.
#  imported in the top using ( from models import * )  #
# +++++ USE FLASK DB INIT THEN MIGRATE THEN UPGRADE TO GENERATE THE TABLES++++++ #


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#
def format_datetime(value, format="medium"):
    date = dateutil.parser.parse(value)
    if format == "full":
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == "medium":
        format = "EE MM, dd, y h:mma"
    # type: ignore
    return babel.dates.format_datetime(date, format, locale="en")


app.jinja_env.filters["datetime"] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route("/")
def index():
    return render_template("pages/home.html")


#  Venues
#  ----------------------------------------------------------------
@app.route("/venues")
def venues():
    venue_display = Venue.query.all()
    data = []
    for venue in venue_display:
        area_venues = (
            Venue.query.filter_by(state=venue.state).filter_by(
                city=venue.city).all()
        )
        venue_data = []
        for venue in area_venues:
            venue_data.append(
                {
                    # referring to venues.html tags#
                    "id": venue.id,
                    "name": venue.name,
                    # used count()to sum the number of shows#
                    "num_upcoming_shows": Show.query.count(),
                }
            )
            # to show details on city,state and venues on venues main page#
        data.append(
            {"city": venue.city, "state": venue.state, "venues": venue_data})
    return render_template(
        "pages/venues.html", areas=data
    )  # areas referres to venues.html#


@app.route("/venues/search", methods=["POST"])
def search_venues():
    search_term = request.form.get("search_term", "")
    search_result = (
        db.session.query(Venue).filter(
            Venue.name.ilike(f"%{search_term}%")).all()
    )
    data = []
    for result in search_result:
        data.append(
            {
                "id": result.id,
                "name": result.name,
                "num_upcoming_shows": len(
                    db.session.query(Show)
                    .filter(Show.venue_id == result.id)
                    .filter(Show.start_time > datetime.now())
                    .all()
                ),
            }
        )
    response = {
        "count": 1,
        "data": [
            {
                "id": 2,
                "name": "The Dueling Pianos Bar",
                "num_upcoming_shows": 0,
            }
        ],
    }
    return render_template(
        "pages/search_venues.html",
        results=response,
        search_term=request.form.get("search_term", ""),
    )


# display page according to venue
@app.route("/venues/<int:venue_id>")
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    venue = Venue.query.get(venue_id)
    if not venue:
        return render_template("errors/404.html")
    upcoming_shows_query = (
        db.session.query(Show)
        .join(Artist)
        .filter(Show.venue_id == venue_id)
        .filter(Show.start_time > datetime.now())
        .all()
    )
    upcoming_shows = []

    past_shows_query = (
        db.session.query(Show)
        .join(Artist)
        .filter(Show.venue_id == venue_id)
        .filter(Show.start_time < datetime.now())
        .all()
    )
    past_shows = []
    for show in past_shows_query:
        past_shows.append(
            {
                "artist_id": show.artist_id,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )
    for show in upcoming_shows_query:
        upcoming_shows.append(
            {
                "artist_id": show.artist_id,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )
    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }
    return render_template("pages/show_venue.html", venue=data)


#  Create Venue
#  ----------------------------------------------------------------


@app.route("/venues/create", methods=["GET"])
def create_venue_form():
    form = VenueForm()
    return render_template("forms/new_venue.html", form=form)


#  Creating Venue
# -----------------------------------------------------------------
@app.route("/venues/create", methods=["POST"])
def create_venue_submission():
    try:
        form = VenueForm(request.form)
        venue = Venue(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            address=form.address.data,
            phone=form.phone.data,
            genres=form.genres.data,
            facebook_link=form.facebook_link.data,
            image_link=form.image_link.data,
        )
        db.session.add(venue)
        db.session.commit()
        flash("Venue: {0} created successfully".format(venue.name))
    except Exception as err:
        flash(
            "An error occurred creating the Venue: {0}. Error: {1}".format(err))
        db.session.rollback()
    return render_template("pages/home.html")


# DELETING VENUE
@app.route("/venues/<venue_id>", methods=["DELETE"])
def delete_venue(venue_id):
    error = False
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash(f"An error occurred. Venue {venue_id} could not be deleted")
    if not error:
        flash(f"the Venue {venue_id} was successfully deleted")
    return render_template("pages/home.html")


#  Artists
#  ----------------------------------------------------------------
@app.route("/artists")
def artists():
    data = db.session.query(Artist).all()
    return render_template("pages/artists.html", artists=data)


# SEARTCHING FOR ARTIST
@app.route("/artists/search", methods=["POST"])
def search_artists():
    search_term = request.form.get("search_term", "")
    search_result = (
        db.session.query(Artist).filter(
            Artist.name.ilike(f"%{search_term}%")).all()
    )
    data = []
    for result in search_result:
        data.append(
            {
                "id": result.id,
                "name": result.name,
                "num_upcoming_shows": len(
                    db.session.query(Show)
                    .filter(Show.artist_id == result.id)
                    .filter(Show.start_time > datetime.now())
                    .all()
                ),
            }
        )
    response = {"count": len(search_result), "data": data}

    return render_template(
        "pages/search_artists.html",
        results=response,
        search_term=request.form.get("search_term", ""),
    )


@app.route("/artists/<int:artist_id>")
def show_artist(artist_id):
    artist_query = db.session.query(Artist).get(artist_id)
    if not artist_query:
        return render_template("errors/404.html")

    past_shows_query = (
        db.session.query(Show)
        .join(Venue)
        .filter(Show.artist_id == artist_id)
        .filter(Show.start_time > datetime.now())
        .all()
    )
    past_shows = []
    for show in past_shows_query:
        past_shows.append(
            {
                "venue_id": show.venue_id,
                "venue_name": show.venue.name,
                "artist_image_link": show.venue.image_link,
                "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )
    upcoming_shows_query = (
        db.session.query(Show)
        .join(Venue)
        .filter(Show.artist_id == artist_id)
        .filter(Show.start_time > datetime.now())
        .all()
    )
    upcoming_shows = []
    for show in upcoming_shows_query:
        upcoming_shows.append(
            {
                "venue_id": show.venue_id,
                "venue_name": show.venue.name,
                "artist_image_link": show.venue.image_link,
                "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )
    data = {
        "id": artist_query.id,
        "name": artist_query.name,
        "genres": artist_query.genres,
        "city": artist_query.city,
        "state": artist_query.state,
        "phone": artist_query.phone,
        "website": artist_query.website,
        "facebook_link": artist_query.facebook_link,
        "seeking_venue": artist_query.seeking_venue,
        "seeking_description": artist_query.seeking_description,
        "image_link": artist_query.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }
    return render_template("pages/show_artist.html", artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route("/artists/<int:artist_id>/edit", methods=["GET"])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)

    if artist:
        form.name.data = artist.name
        form.city.data = artist.city
        form.state.data = artist.state
        form.phone.data = artist.phone
        form.genres.data = artist.genres
        form.facebook_link.data = artist.facebook_link
        form.image_link.data = artist.image_link
        form.website.data = artist.website
        form.seeking_venue.data = artist.seeking_venue
        form.seeking_description.data = artist.seeking_description

    return render_template("forms/edit_artist.html", form=form, artist=artist)


# CREATE ARTIST
@app.route("/artists/<int:artist_id>/edit", methods=["POST"])
def edit_artist_submission(artist_id):
    error = False
    artist = Artist.query.get(artist_id)
    try:
        artist.name = request.form["name"]
        artist.city = request.form["city"]
        artist.state = request.form["state"]
        artist.phone = request.form["phone"]
        artist.genres = request.form.getlist("genres")
        artist.image_link = request.form["image_link"]
        artist.facebook_link = request.form["facebook_link"]
        artist.website = request.form["website"]
        artist.seeking_venue = True if "seeking_venue" in request.form else False
        artist.seeking_description = request.form["seeking_description"]

        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash("there was an error occurre, Artist could not be changed")
    if not error:
        flash("Artist was successfully updated")
    return redirect(url_for("show_artist", artist_id=artist_id))


# SHOW VENUES
@app.route("/venues/<int:venue_id>/edit", methods=["GET"])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    if venue:
        form.name.data = venue.name
        form.city.data = venue.city
        form.state.data = venue.state
        form.phone.data = venue.phone
        form.address.data = venue.address
        form.genres.data = venue.genres
        form.facebook_link.data = venue.facebook_link
        form.image_link.data = venue.image_link
        form.website.data = venue.website
        form.seeking_talent.data = venue.seeking_talent
        form.seeking_description.data = venue.seeking_description

    return render_template("forms/edit_venue.html", form=form, venue=venue)


# CREATE VENUE
@app.route("/venues/<int:venue_id>/edit", methods=["POST"])
def edit_venue_submission(venue_id):
    error = False
    venue = Venue.query.get(venue_id)

    try:
        venue.name = request.form["name"]
        venue.city = request.form["city"]
        venue.state = request.form["state"]
        venue.address = request.form["address"]
        venue.phone = request.form["phone"]
        venue.genres = request.form.getlist("genres")
        venue.image_link = request.form["image_link"]
        venue.facebook_link = request.form["facebook_link"]
        venue.website = request.form["website"]
        venue.seeking_talent = True if "seeking_talent" in request.form else False
        venue.seeking_description = request.form["seeking_description"]

        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash(f"An error occurred. Venue could not be changed.")
    if not error:
        flash(f"Venue was successfully updated!")
    return redirect(url_for("show_venue", venue_id=venue_id))


#  Create new Artist
#  ----------------------------------------------------------------

@app.route("/artists/create", methods=["GET"])
def create_artist_form():
    form = ArtistForm()
    return render_template("forms/new_artist.html", form=form)

#  creating new artist


@app.route("/artists/create", methods=["POST"])
def create_artist_submission():
    flash("Artist " + request.form["name"] + " was successfully listed!")
    error = False
    try:
        name = request.form["name"]
        city = request.form["city"]
        state = request.form["state"]
        phone = request.form["phone"]
        genres = (request.form.getlist("genres"),)
        facebook_link = request.form["facebook_link"]
        image_link = request.form["image_link"]
        website = request.form["website"]
        seeking_venue = True if "seeking_venue" in request.form else False
        seeking_description = request.form["seeking_description"]

        artist = Artist(
            name=name,
            city=city,
            state=state,
            phone=phone,
            genres=genres,
            facebook_link=facebook_link,
            image_link=image_link,
            website=website,
            seeking_venue=seeking_venue,
            seeking_description=seeking_description,
        )
        db.session.add(artist)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash(
            "An error occurred. Artist "
            + request.form["name"]
            + " could not be listed."
        )
    if not error:
        # on successful db insert, flash success
        flash("Artist " + request.form["name"] + " was successfully listed!")
    return render_template("pages/home.html")


#  Shows
#  ----------------------------------------------------------------

@app.route("/shows")
def shows():
    # displays list of shows at /shows
    shows_query = db.session.query(Show).join(Artist).join(Venue).all()
    data = []
    for show in shows_query:
        data.append(
            {
                "venue_id": show.venue_id,
                "venue_name": show.venue.name,
                "artist_id": show.artist_id,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

    return render_template("pages/shows.html", shows=data)

# CREATE SHOW


@app.route("/shows/create")
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template("forms/new_show.html", form=form)

# CREATE SHOW


@app.route("/shows/create", methods=["POST"])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    error = False
    try:
        artist_id = request.form["artist_id"]
        venue_id = request.form["venue_id"]
        start_time = request.form["start_time"]

        print(request.form)
        show = Show(artist_id=artist_id, venue_id=venue_id,
                    start_time=start_time)
        db.session.add(show)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        # on unsuccessful db insert, flash an error instead.
        flash("An error occurred. Show could not be listed.")
    if not error:
        # on successful db insert, flash success
        flash("Show was successfully listed")
    return render_template("pages/home.html")


@app.errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("errors/500.html"), 500


if not app.debug:
    file_handler = FileHandler("error.log")
    file_handler.setFormatter(
        Formatter(
            "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info("errors")

# enabling debug mode....
if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0")
