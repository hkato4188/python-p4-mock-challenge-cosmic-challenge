from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)


class Planet(db.Model, SerializerMixin):
    __tablename__ = 'planets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    distance_from_earth = db.Column(db.Integer)
    nearest_star = db.Column(db.String)

    # Add relationship
    missions = db.relationship(
        'Mission', backref='planet')
    # Add serialization rules
    serialize_rules = ("-missions.planet",)


class Scientist(db.Model, SerializerMixin):
    __tablename__ = 'scientists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    field_of_study = db.Column(db.String)

    # Add relationshipmis
    missions = db.relationship(
        'Mission', backref='scientist')
    # Add serialization rules
    serialize_rules = ("-missions.scientist",)
    # Add validation

    @validates('name', 'field_of_study')
    def validate_name(self, db_column, value):
        if db_column == 'name':
            if type(value) == str and len(value) > 0:
                return value
            else:
                raise ValueError('A scientist needs a name of type string')
        elif db_column == 'field_of_study':
            if type(value) == str and len(value) > 0:
                return value
            else:
                raise ValueError(
                    'A scientist needs a field of study that is of type string')


class Mission(db.Model, SerializerMixin):
    __tablename__ = 'missions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    # Add relationships
    scientist_id = db.Column(db.Integer, db.ForeignKey('scientists.id'))
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'))
    # Add serialization rules
    serialize_rules = ("-planet.missions", "-scientist.missions")
    # Add validation

    @validates('name')
    def validate_name(self, db_column, name):
        if name and len(name) > 0:
            return name
        else:
            raise ValueError('A mission must have a name')

    @validates('scientist_id')
    def validate_scientist_id(self, db_column, scientist_id):
        scientist = Scientist.query.filter(Scientist.id == scientist_id)
        if not scientist or scientist_id == None:
            raise ValueError('A mission must have a valid scientist id')
        else:
            return scientist_id

    @validates('planet_id')
    def validate_planet_id(self, db_column, planet_id):
        planet = Planet.query.filter(Planet.id == planet_id)
        if not planet or planet_id == None:
            raise ValueError('A mission must have a valid planet id')
        else:
            return planet_id


# add any models you may need.
