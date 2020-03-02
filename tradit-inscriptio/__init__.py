# -*- coding: utf-8 -*-
"""Main application package."""

# init.py

from flask import Flask, render_template, session
import smtplib

engine = sa.create_engine('mssql+pyodbc://user:password@server/database')