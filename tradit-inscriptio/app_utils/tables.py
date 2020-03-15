# import things
from flask_table import Table, Col, LinkCol
from flask import url_for


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
    classes = ['table', 'table-striped', 'table-responsive', 'table-hover', 'mx-auto', ' w-auto']
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
