from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

URL = "https://openlibrary.org/"

app = Flask(__name__)
app.config["SECRET_KEY"] = "8BYkEfBA6O6donzWlSihBXox7C0sKR6b"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///book.db"

bootstrap = Bootstrap5(app)
db = SQLAlchemy(app)


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    year = db.Column(db.Integer, nullable=True)
    description = db.Column(db.String(500), nullable=True)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable=False)


with app.app_context():
    db.create_all()


class RateBookForm(FlaskForm):
    rating = StringField("Your rating out of 10")
    review = StringField("Your Review")
    submit = SubmitField("Done")


@app.route("/")
def home():
    result = db.session.execute(db.select(Book))
    all_books = result.scalars().all()
    print(all_books)
    return render_template("index.html", books=all_books)


@app.route("/edit", methods=["POST", "GET"])
def edit_book():
    form = RateBookForm()
    book_id = request.args.get("id")
    book = db.get_or_404(Book, book_id)
    if form.validate_on_submit():
        book.rating = float(form.rating.data)
        book.review = form.review.data
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("edit.html", book=book, form=form)


@app.route("/delete")
def delete_book():
    book_id = request.args.get("id")
    book = db.get_or_404(Book, book_id)
    db.session.delete(book)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/add", methods=["POST", "GET"])
def add():
    return


if __name__ == "__main__":
    """Run the Flask application"""
    app.run(debug=True)
