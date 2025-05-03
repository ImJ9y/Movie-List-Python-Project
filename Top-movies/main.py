from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
import requests


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)

# CREATE DB
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///Movies.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

headers = {
            "accept": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJlMjc2NmQ1MThkMDA5Y2EwYzAzMzhhZGY0ZWEyMDIzMSIsIm5iZiI6MTc0NTk5NTA2Ni43ODksInN1YiI6IjY4MTFjNTNhYWY3NTFiNGIwMTYxNmRlOSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.W-2IJmFf2TKXv64xee9mGglJwtVLbNp2R69KsNsi8f4"
        }

# CREATE TABLE
class Movies(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(250), nullable=False)
    year = db.Column(db.Integer,  nullable=False)
    description = db.Column(db.String(250),nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer,  nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable=False)

@app.route("/")
def home():
    result = db.session.execute(db.select(Movies).order_by(Movies.rating))
    all_movies = result.scalars().all()  # convert ScalarResult to Python List

    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()

    return render_template("index.html", movies=all_movies)

class CreateMovieForm(FlaskForm):
    title = StringField("Movie Title")
    submit = SubmitField("Add Movie")

@app.route("/add", methods=["GET", "POST"])
def add():
    form = CreateMovieForm()

    if form.validate_on_submit():
        new_movie_title = form.title.data
        url = "https://api.themoviedb.org/3/search/movie"
        response = requests.get(url, headers=headers, params={"query": new_movie_title})
        data = response.json()["results"]

        return render_template("select.html", options=data)

    return render_template("add.html", form=form)

class RateMovieForm(FlaskForm):
    rating = StringField("Your Rating Out of 10 e.g. 7.5")
    review = StringField("Your Review")
    submit = SubmitField("Done")

@app.route("/edit", methods=["GET", "POST"])
def edit():
    form = RateMovieForm()
    movie_id = request.args.get("id")
    movie = Movies.query.get(movie_id)

    if form.validate_on_submit():
        movie.rating = float(form.rating.data)
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))

    return render_template("edit.html", form=form)

@app.route("/delete")
def delete():
    movie_id = request.args.get("id")
    movie_to_delete = Movies.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()

    return redirect(url_for('home'))

@app.route("/find")
def find_movie():
    movie_api_id = request.args.get("id")

    if movie_api_id:
        movie_detail_url = f"https://api.themoviedb.org/3/movie/{movie_api_id}"
        response = requests.get(movie_detail_url, headers=headers)
        data = response.json()
        new_movie = Movies(
            title=data["title"],
            # The data in release_date includes month and day, we will want to get rid of.
            year=data["release_date"].split("-")[0],
            img_url=f"https://image.tmdb.org/t/p/w500{data["poster_path"]}",
            description=data["overview"]
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for("home"))

if __name__ == '__main__':
    app.run(debug=True)
