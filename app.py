# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

from create_data import Movie, Director, Genre

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

api = Api(app)


class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    director_id = fields.Int()
    genre_id = fields.Int()


class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()


class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()


movie_ns = api.namespace('movies')
director_ns = api.namespace('directors')
genre_ns = api.namespace('genres')


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)

genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)


# ========== Movie ==========

@movie_ns.route('/')
class MoviesView(Resource):

    def get(self, page=1):
        movies_query = db.session.query(Movie)
        director_id = request.args.get('director_id')
        if director_id is not None:
            movies_query = movies_query.filter(Movie.director_id == director_id)

        genre_id = request.args.get('genre_id')
        if genre_id is not None:
            movies_query = movies_query.filter(Movie.genre_id == genre_id)

        movies = movies_query.paginate(page, per_page=5)

        return movies_schema.dump(movies.items), 200

    def post(self):
        new_movie = Movie(**request.json)

        with db.session.begin():
            db.session.add(new_movie)

        return "", 201


@movie_ns.route('/<int:uid>')
class MovieView(Resource):

    def get(self, uid: int):
        movie = db.session.query(Movie).get(uid)
        if not movie:
            return "", 404
        return movie_schema.dump(movie), 200

    def put(self, uid: int):
        movie = db.session.query(Movie).get(uid)
        # movie = db.session.query(Movie).filter(Movie.id == uid).update(request.json)

        # if movie != 1:
        #     return "", 400

        new_movie = request.json
        movie.title = new_movie.get('title')
        movie.description = new_movie.get('description')
        movie.trailer = new_movie.get('trailer')
        movie.year = new_movie.get('year')
        movie.rating = new_movie.get('rating')
        #
        # db.session.add(movie)
        db.session.commit()

        return "", 204

    def delete(self, uid: int):
        movie = db.session.query(Movie).get(uid)

        if not movie:
            return "", 400
        db.session.delete(movie)
        db.session.commit()
        return "", 204


# ========== Directors ==========

@director_ns.route('/')
class DirectorsView(Resource):

    def get(self):
        directors_query = db.session.query(Director)
        return directors_schema.dump(directors_query), 200

    def post(self):
        new_director = Director(**request.json)

        with db.session.begin():
            db.session.add(new_director)

        return "", 201


@director_ns.route('/<int:uid>')
class DirectorView(Resource):

    def get(self, uid: int):
        director = db.session.query(Director).get(uid)
        if not director:
            return "", 404
        return director_schema.dump(director), 200

    def put(self, uid: int):
        director = db.session.query(Director).filter(Director.id == uid).update(request.json)
        db.session.commit()
        if director != 1:
            return "", 400
        return "", 204

    def delete(self, uid: int):
        director = db.session.query(Director).get(uid)

        if not director:
            return "", 400
        db.session.delete(director)
        db.session.commit()
        return "", 204


# =========== Genres ============
@genre_ns.route('/')
class GenresView(Resource):

    def get(self):
        genres_query = db.session.query(Genre)
        return genres_schema.dump(genres_query.all()), 200

    def post(self):
        new_genre = Genre(**request.json)

        with db.session.begin():
            db.session.add(new_genre)

        return "", 201


@genre_ns.route('/<int:uid>')
class GenreView(Resource):

    def get(self, uid: int):
        genre = db.session.query(Genre).get(uid)
        if not genre:
            return "", 404
        return genre_schema.dump(genre), 200

    def put(self, uid: int):
        genre = db.session.query(Genre).filter(Genre.id == uid).update(request.json)
        db.session.commit()
        if genre != 1:
            return "", 400
        return "", 204

    def delete(self, uid: int):
        genre = db.session.query(Genre).get(uid)

        if not genre:
            return "", 400
        db.session.delete(genre)
        db.session.commit()
        return "", 204



if __name__ == '__main__':
    app.run(debug=True)
