from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
import requests

URL = "https://openlibrary.org/"
app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/edit", methods=["POST", "GET"])
def edit():
    return


@app.route("/delete")
def delete():
    return


@app.route("/add", methods=["POST", "GET"])
def add():
    return


if __name__ == "__main__":
    """Run the Flask application"""
    app.run(debug=True)
