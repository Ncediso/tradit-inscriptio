from flask import Blueprint, render_template, flash, redirect, request, Markup, jsonify, url_for
from ..app_utils import tables as table_utils
# Results, get_reports, format_table_head, format_table_body, get_clients
from ..app_utils.db_setup import db_session
from ..models.models import Report, Client
import requests
import json

import pandas as pd


tables = Blueprint('tables', __name__)


@tables.route("/tables")
def show_tables():
    data = pd.read_excel('dummy_data.xlsx')
    data.set_index(['Name'], inplace=True)
    data.index.name = None
    females = data.loc[data.Gender == 'f']
    males = data.loc[data.Gender == 'm']
    return render_template(
        'view.html', tables=[
            females.to_html(classes='female'),
            males.to_html(classes='male')],
        titles=['na', 'Female surfers', 'Male surfers'])


@tables.route("/reports")
def show_reports():
    items = table_utils.get_reports()

    table = table_utils.Results(items)
    table_head = table_utils.format_table_head(table)
    table_body = table_utils.format_table_body(table)

    client_list = [('-1', 'All Clients')] + table_utils.get_clients()
    default = '-1'

    return render_template(
        'tables.html', table_head=table_head, table_body=table_body,
        clients=client_list, default=default)


@tables.route("/reports/<client_id>")
def show_clients_reports(client_id):
    client_id_int = int(json.loads(client_id, parse_int=int))
    items = table_utils.get_reports(client_id)

    table = table_utils.Results(items)
    table_head = table_utils.format_table_head(table)
    table_body = table_utils.format_table_body(table)

    client_list = table_utils.get_clients()
    data = [item for item in client_list if item[0] == client_id_int]
    client_list = [('-1', 'All Clients')] + data + client_list
    default = data[0][0]

    return render_template(
        'tables.html', table_head=table_head, table_body=table_body,
        clients=client_list, default=default)


@tables.route('/post-filter-report', methods=['POST'])
def filter_reports():
    js_data = request.form['canvas_data']
    js_object = int(json.loads(js_data, parse_int=int))
    if js_object != -1:
        return redirect(url_for('tables.show_clients_reports', client_id=js_object))
    else:
        return redirect(url_for('tables.show_reports'))


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
        table = table_utils.Results(results)
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



#
# export FLASK_APP=tradit-inscriptio/
# export FLASK_ENV=Development
# export FLASK_DEBUG=1
# export FLASK_RUN_PORT=5000
