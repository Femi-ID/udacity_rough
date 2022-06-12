# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel, sys
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from datetime import datetime
from flask_wtf import Form
from models import Artist, Venue, Show
from models import db

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
# db.init_app(app)
migrate = Migrate(app, db)


# DONE: connect to a local postgresql database

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#


# TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    data = []
    venue_info = Venue.query.all()
    venue_dictionary = {}

    for venue in venue_info:
        value = f'{venue.city}, {venue.state}'
        # venue.add((venue.city, venue.state))

        venue_dictionary.setdefault(value, []).append({
            "id": venue.id,
            "city": venue.city,
            "state": venue.state,
            "num_upcoming_shows": len(venue.shows),
        })

    for info in venue_dictionary.values():
        data.append({
            'city': info[0]['city'],
            'state': info[0]['state'],
            'venues': info
        })
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # search for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search = request.form.get('search_term')
    response = Venue.query.filter(Venue.name.ilike(f'%{search}%') | Venue.state.ilike(f'%{search}%') | Venue.city.ilike(f'%{search}%'))

    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id

    venue_data = Venue.query.filter_by(id=venue_id).all()
    upcoming_shows_data = Show.query.join(Venue).filter_by(id=venue_id).filter(Show.show_time > datetime.utcnow())
    past_shows_data = Show.query.join(Venue).filter_by(id=venue_id).filter(Show.show_time <= datetime.utcnow())

    return render_template('pages/show_venue.html', venue=venue_data, upcoming_shows=upcoming_shows_data,
                           past_shows=past_shows_data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    venue_form = VenueForm(request.form)
    new_input = request.form
    if venue_form.validate():
        try:
            new_venue = Venue(name=new_input['name'], city=new_input['city'], state=new_input['state'],
                              address=new_input['address'], phone=new_input['phone'],
                              genres=request.form.getlist('genres'), website_link=new_input['website_link'],
                              facebook_link=new_input['facebook_link'],
                              seeking_talent=venue_form.seeking_talent.data,
                              seeking_description=new_input['seeking_description'])
            db.session.add(new_venue)
            db.session.commit()
            error = False
            flash('Venue ' + request.form['name'] + ' was successfully listed!')
        except:
            db.session.rollback()
            error = True
        finally:
            db.session.close()
        if error:
            flash('An error occurred. Venue ' + venue_form.name.data + ' could not be listed.')
            return render_template('pages/home.html')
        else:
            flash('Please try again')

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    venue_query = Venue.query.filter(Venue.id == venue_id).delete()
    error = False
    try:
        db.session.delete(venue_query)
        db.session.commit()
        flash('Venue was successfully deleted!')
        return render_template('pages/home.html')

    except:
        db.session.rollback()
        # error = True
    finally:
        db.session.close()

    if error:
        flash(f'An error occurred, {venue_query.name} could not be deleted')
        return render_template('pages/home.html')
    else:
        flash('Please try again')
        return redirect(url_for('index'))

    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database

    artists_query = Artist.query.all()
    data = []
    for artist in artists_query:
        data_dictionary = {
            "id": artist.id,
            "name": artist.name
        }

        data.append(data_dictionary)
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    response = {
        "count": 1,
        "data": [{
            "id": 4,
            "name": "Guns N Petals",
            "num_upcoming_shows": 0,
        }]
    }

    search = request.form.get('search_term', '')
    artist_query = Artist.query.filter(Artist.name.ilike(f'%{search}%')) | Artist.id.ilike(f'%{search}%') | \
                   Artist.shows.ilike(f'%{search}%')

    response = {
        "count": len(artist_query),
        "data": []
    }

    for artist_info in artist_query:
        response["data"].append({
            "id": artist_info.id,
            "name": artist_info.name,
            "num_upcoming_shows": len(artist_info.shows)
        })

    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    artist_data = Artist.query.get(artist_id)
    upcoming_shows = Show.query.join(Artist).filter_by(id=artist_id).filter(Show.show_time > datetime.utcnow())
    past_shows = Show.query.join(Artist).filter_by(id=artist_id).filter(Show.show_time <= datetime.utcnow())
    past_shows_count = len(past_shows)
    upcoming_shows_count = len(upcoming_shows)
    return render_template('pages/show_artist.html', artist=artist_data, upcoming_shows=upcoming_shows_count,
                           past_shows=past_shows_count)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist_query = Artist.query.filter_by(id=artist_id).all()

    form.name.data = artist_query.name
    form.city.data = artist_query.city
    form.state.data = artist_query.state
    form.genres.data = artist_query.genres
    form.phone.data = artist_query.phone
    form.website_link.data = artist_query.website
    form.facebook_link.data = artist_query.facebook_link
    form.image_link.data = artist_query.image_link
    form.seeking_description.data = artist_query.seeking_description
    form.seeking_venue.data = artist_query.seeking_venue

    #     artist_info = {
    #         "id": artist.id,
    #         "name": artist.name,
    #         "genres": artist.genres,
    #         "city": artist.city,
    #         "state": artist.state,
    #         "phone": artist.phone,
    #         "image_link": artist.image_link,
    #         "website": artist.website,
    #         "facebook_link": artist.facebook_link,
    #         "seeking_venue": artist.seeking_venue,
    #         "seeking_description": artist.seeking_description,
    #     }

    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist_query)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    form = ArtistForm(request.form)
    artist_query = Artist.query.get(artist_id)
    if form.validate():
        try:
            artist_query.name = form.name.data
            artist_query.city = form.city.data
            artist_query.state = form.state.data
            artist_query.phone = form.phone.data
            artist_query.genres = form.genres.data
            artist_query.facebook_link = form.facebook_link.data
            artist_query.website_link = form.website_link.data
            artist_query.image_link = form.image_link.data
            artist_query.seeking_description = form.seeking_description.data
            artist_query.looking_for_venues = form.seeking_venue.data
            db.session.commit()
            flash('Artist: ' + artist_query.name + ' has been successfully updated!')
        except:
            db.session.rollback()
            flash('An error occurred. Artist ' + artist_query.name + ' could not be updated.')
        finally:
            db.session.close()
        return redirect(url_for('show_artist', artist_id=artist_id))
    else:
        flash('An error has occurred, Please try again')
        return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.filter_by(id=venue_id).all()

    form.name.data = venue.name
    form.state.data = venue.state
    form.phone.data = venue.phone
    form.address.data = venue.address
    form.city.data = venue.city
    form.genres.data = venue.genres
    form.image_link.data = venue.image_link
    form.seeking_talent.data = venue.seeking_talent # I need to cross-check this
    form.facebook_link.data = venue.facebook_link
    form.website_link.data = venue.website_link
    form.seeking_description.data = venue.seeking_description

    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    form = VenueForm(request.form)
    if form.validate():
        venue = Venue.query.get(venue_id)
        try:
            venue.name = form.name.data
            venue.city = form.city.data
            venue.state = form.state.data
            venue.genres = form.genres.data
            venue.phone = form.phone.data
            venue.address = form.address.data
            venue.image_link = form.image_link.data
            venue.facebook_link = form.facebook_link.data
            venue.seeking_talent = form.seeking_talent.data
            venue.website_link = form.website_link.data
            venue.seeking_description = form.seeking_description.data
            db.session.commit()
            flash('Venue: ' + form.name.data + ' has been successfully updated!')
        except:
            db.session.rollback()
            flash('An error has occurred. Please try again')
        finally:
            db.session.close()
        return redirect(url_for('show_venue', venue_id=venue_id))
    else:
        flash('Please check all fields and retry')
    # TODO: take values from the form submitted, and update existing
    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    form = ArtistForm(request.form)

    if form.validate():

        try:
            artist_name = form.name.data
            artist_city = form.city.data
            artist_state = form.state.data
            artist_phone = form.phone.data
            artist_image_link = form.image_link.data
            artist_facebook_link = form.facebook_link.data
            artist_website_link = form.website_link.data
            artist_seeking_description = form.seeking_description.data
            seeking_venue = form.seeking_venue.data

            new_artist = Artist(name=artist_name, city=artist_city, state=artist_state, phone=artist_phone,
                                image_link=artist_image_link, facebook_link=artist_facebook_link, website=artist_website_link,
                                seeking_description=artist_seeking_description, looking_for_venues=seeking_venue,
                                genres=request.form.getlist('genres'))

            db.session.add(new_artist)
            db.session.commit()
            flash('Artist ' + form.name.data + ' was successfully listed!')
            return render_template('pages/home.html')
        except:
            db.session.rollback()
            flash('Artist:' + form.name.data + ' could not listed. Please try again')
            print(sys.exc_info())
            return redirect(url_for('index'))

        finally:
            db.session.close()

    else:
        flash('Please re-check all fields and try again.')
        return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    data = Show.query.all()
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead

    form = ShowForm(request.form)
    if form.validate():

        try:
            artist_id = form.artist_id.data
            artist = Artist.query.get(artist_id)
            venue_id = form.venue_id.data
            show_time = form.start_time.data

            show = Show(artist_id=artist_id, venue_id=venue_id, start_time=show_time)
            db.session.add(show)
            db.session.commit()
            flash('Show has been successfully listed!')
            error = False
            return redirect(url_for('index'))
        except:
            db.session.rollback()
            error = True
        finally:
            db.session.close()
        if error:
            flash('An has error occurred, please check your details and retry.')
            return render_template('pages/home.html')

    else:
        flash('An has error occurred, please check your details and retry.')
        return render_template('pages/home.html')

    # on successful db insert, flash success
    flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
