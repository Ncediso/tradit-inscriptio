from flask import Blueprint, render_template, flash, redirect, request
from ..app_utils.tables import Results
from ..app_utils.db_setup import db_session
from ..models.models import Report
import requests

import pandas as pd


tables = Blueprint('tables', __name__)


@tables.route("/tables")
def show_tables():
    data = pd.read_excel('dummy_data.xlsx')
    data.set_index(['Name'], inplace=True)
    data.index.name=None
    females = data.loc[data.Gender == 'f']
    males = data.loc[data.Gender == 'm']
    return render_template(
        'view.html',
        tables=[
            females.to_html(classes='female'),
            males.to_html(classes='male')],
        titles=['na', 'Female surfers', 'Male surfers'])


@tables.route('/results')
def search_results(search):
    results = []
    search_string = search.data['search']

    if search.data['search'] == '':
        qry = db_session.query(Report)
        results = qry.all()

    if not results:
        flash('No results found!')
        return redirect('/')
    else:
        # display results
        table = Results(results)
        table.border = True
        return render_template('results.html', table=table)


# @tables.route('/item/<int:id>', methods=['GET', 'POST'])
# def edit(id):
#     qry = db_session.query(Report).filter(
#                 Report.id==id)
#     album = qry.first()
#     if album:
#         form = AlbumForm(formdata=request.form, obj=album)
#         if request.method == 'POST' and form.validate():
#             # save edits
#             save_changes(album, form)
#             flash('Album updated successfully!')
#             return redirect('/')
#         return render_template('edit_album.html', form=form)
#     else:
#         return 'Error loading #{id}'.format(id=id)


def save_changes(album, form, new=False):
    """
    Save the changes to the database
    """
    # Get data from form and assign it to the correct attributes
    # of the SQLAlchemy table object
    # artist = Artist()
    # artist.name = form.artist.data
    # album.artist = artist
    # album.title = form.title.data
    # album.release_date = form.release_date.data
    # album.publisher = form.publisher.data
    # album.media_type = form.media_type.data
    if new:
        # Add the new album to the database
        db_session.add(album)
    # commit the data to the database
    db_session.commit()