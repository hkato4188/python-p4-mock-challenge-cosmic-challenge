#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return 'We are home!'


@app.route('/scientists', methods=["GET", "POST"])
def scientists():
    if request.method == "GET":
        all_scientists = [s.to_dict(only=("id", "name", "field_of_study"))
                          for s in Scientist.query.all()]
        return make_response(all_scientists, 200)
    elif request.method == "POST":
        data = request.get_json()
        try:
            new_scientist = Scientist(
                name=data['name'],
                field_of_study=data['field_of_study']
            )
            db.session.add(new_scientist)
            db.session.commit()
            json_scientist = new_scientist.to_dict(
                rules=("-signups", "-missions"))
            return make_response(json_scientist, 201)
        except:
            return make_response({"errors": ["validation errors"]}, 400)


@app.route('/scientists/<int:id>', methods=["GET", "PATCH", "DELETE"])
def scientist(id):
    scientist = Scientist.query.filter(Scientist.id == id).first()
    if scientist:
        if request.method == "GET":
            return make_response(scientist.to_dict(), 200)
        elif request.method == "PATCH":
            data = request.get_json()
            try:
                for attr in data:
                    setattr(scientist, attr, data[attr])
                db.session.add(scientist)
                db.session.commit()
                return make_response(scientist.to_dict(rules=("-signups", "-missions")), 202)
            except:
                return make_response({"errors": ["validation errors"]}, 400)
        elif request.method == "DELETE":
            for mission in scientist.missions:
                db.session.delete(mission)
            db.session.delete(scientist)
            db.session.commit()
            return make_response({}, 204)
    else:
        return make_response({"error": "Scientist not found"}, 404)


@app.route('/planets', methods=["GET"])
def planets():
    all_planets = [p.to_dict(only=(
        "id", "name", "distance_from_earth", "nearest_star")) for p in Planet.query.all()]
    return make_response(all_planets, 200)


@app.route('/missions', methods=["GET", "POST"])
def missions():
    if request.method == "GET":
        all_missions = [m.to_dict(rules=("-scientist", "-planet"))
                        for m in Mission.query.all()]
        return make_response(all_missions, 200)
    elif request.method == "POST":
        try:
            data = request.get_json()
            new_mission = Mission(
                name=data['name'],
                scientist_id=data['scientist_id'],
                planet_id=data['planet_id']
            )
            db.session.add(new_mission)
            db.session.commit()
            return make_response(new_mission.to_dict(), 201)
        except:
            return make_response({"errors": ["validation errors"]}, 400)


if __name__ == '__main__':
    app.run(port=5555, debug=True)
