# import things
from flask_table import Table, Col, LinkCol
from flask import url_for, Markup
from ..models.models import Report, Client
from sqlalchemy.orm import load_only


# Declare your table
class ItemTable(Table):
    name = Col('Name')
    description = Col('Description')


# Get some objects
class Item(object):
    def __init__(self, name, description):
        self.name = name
        self.description = description


items = [Item('Name1', 'Description1'),
         Item('Name2', 'Description2'),
         Item('Name3', 'Description3')]
# # Or, equivalently, some dicts
# items = [dict(name='Name1', description='Description1'),
#          dict(name='Name2', description='Description2'),
#          dict(name='Name3', description='Description3')]
#
# # Or, more likely, load items from your database with something like
# items = ItemModel.query.all()
#
# # Populate the table
# table = ItemTable(items)
#
# # Print the html
# print(table.__html__())
# # or just {{ table }} from within a Jinja template


class Results(Table):
    # classes = ['table', 'table-striped', 'table-responsive', 'table-hover', 'mx-auto', ' w-auto']
    id = Col('Id', show=False)
    report_name = Col('Report Name')
    client_name = Col('Client Name')
    report_date = Col('Report Date')
    value_date = Col('Value Date')
    report_path = Col('Report Path', show=False)
    client_email_address = Col("Client Email Address")
    email_status = Col('Email Status')
    time = Col('Report Date Time')
    is_return_report = Col('Is Rerun Report')

    allow_sort = True

    def sort_url(self, col_key, reverse=False):
        if reverse:
            direction = 'desc'
        else:
            direction = 'asc'
        return url_for('tables.show_reports', sort=col_key, direction=direction)


def get_reports(client_id=None):
    # clients = None
    if client_id:
        reports = Report.query.filter_by(report_date='2020-03-09').join("client").filter_by(id=client_id).all()
        # print(len(reports))
    else:
        reports = Report.query.filter_by(report_date='2020-03-09').join("client").all()
        # print(len(reports))
    data_items = list()
    for report in reports:
        client = Client.get_by_id(report.client_id)
        item = dict(
            id=report.id,
            report_name=report.name,
            client_name=client.name,
            report_date=report.report_date,
            value_date=report.value_date,
            report_path=report.report_path,
            client_email_address=client.email_address,
            email_status=report.email_status,
            time=report.time,
            is_return_report=report.is_return_report
        )
        data_items.append(item)

    return data_items


def format_table_head(table):
    table_head = table.thead()
    table_head = table_head.replace("<tr>", '<tr class="row100 head">')
    table_head = table_head.replace("<th>", '<th class="cell100 column-dynamic">')
    table_head = Markup(table_head)
    return table_head


def format_table_body(table):
    table_body = table.tbody()
    if not table_body:
        # print("No Reports found for the table given.")
        table_body = "<tbody><tr><strong>No Reports found for the table given.</strong></tr></tbody>"
    else:
        table_body = table_body.replace("<tr>", '<tr class="row100 body">')
        table_body = table_body.replace("<td>", '<td class="cell100 column-dynamic">')

    table_body = Markup(table_body)
    return table_body


def get_clients():
    fields = ['id', 'name']
    clients = Client.query.options(load_only(*fields)).all()
    sorted_clients = sorted([(client.id, client.name) for client in clients], key=lambda tub: tub[1])
    return sorted_clients

