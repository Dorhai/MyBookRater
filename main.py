from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
import re

PLACEHOLDER_IMG = (
    "https://developers.elementor.com/docs/assets/img/elementor-placeholder-image.png"
)
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


class FindBookForm(FlaskForm):
    title = StringField("Book Title", validators=[DataRequired()])
    submit = SubmitField("Add Book")


@app.route("/")
def home():
    result = db.session.execute(db.select(Book).order_by(Book.rating.desc()))
    all_books = result.scalars().all()
    for i in range(len(all_books)):
        all_books[i].ranking = i + 1
    db.session.commit()
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
def add_book():
    form = FindBookForm()
    if form.validate_on_submit():
        book_title = form.title.data
        response = requests.get(
            f"https://openlibrary.org/search.json?q={book_title.replace(' ', '+')}"
        )
        if response.status_code == 200:
            list_of_books = response.json()["docs"]
            return render_template("select.html", book_options=list_of_books)
    return render_template("add.html", form=form)


@app.route("/find")
def find_book():
    title = request.args.get("title")
    author = request.args.get("author")
    year = request.args.get("year")
    cover = request.args.get("cover")

    if not title or not author:
        return "Invalid book data", 400  # Prevents adding empty books

    description = "No description available"

    search_url = (
        f"https://openlibrary.org/search.json?q={title.replace(' ', '+')}&limit=1"
    )
    response = requests.get(search_url)

    if response.status_code == 200:
        data = response.json()
        if "docs" in data and len(data["docs"]) > 0:
            work_key = data["docs"][0].get("key", "")  # Extract Work Key
            if work_key:
                work_key = work_key.split("/")[-1]  # Extract only OLxxxxxW
                print(f"📌 Extracted Work Key: {work_key}")

                # ✅ Step 2: Fetch description from Work API
                work_url = f"https://openlibrary.org/works/{work_key}.json"
                work_response = requests.get(work_url)

                if work_response.status_code == 200:
                    work_data = work_response.json()

                    # ✅ Extract description if available
                    if "description" in work_data:
                        if isinstance(work_data["description"], dict):
                            description = work_data["description"].get(
                                "value", "No description available"
                            )
                        else:
                            description = work_data["description"]

                    # ✅ Step 3: Clean Description (Remove text after "(" or "-")
                    description = re.split(r"[\(-]", description)[0].strip()

    # ✅ Step 4: Add book to database with the cleaned description
    print(f"Extracted Work Key: {work_key}")
    new_book = Book(
        title=title,
        author=author,
        year=int(year) if year and year.isdigit() else None,
        description=description,
        img_url=f"https://covers.openlibrary.org/b/id/{cover}-M.jpg"
        if cover
        else PLACEHOLDER_IMG,  # add placeholder
    )

    db.session.add(new_book)
    db.session.commit()
    return redirect(url_for("rate_book", id=new_book.id))


@app.route("/edit", methods=["GET", "POST"])
def rate_book():
    form = RateBookForm()
    book_id = request.args.get("id")
    book = db.get_or_404(Book, book_id)
    if form.validate_on_submit():
        book.rating = float(form.rating.data)
        book.review = form.review.data
        db.session()
        return redirect(url_for("home"))
    return render_template("edit.html", book=book, form=form)


if __name__ == "__main__":
    """Run the Flask application"""
    app.run(debug=True)
