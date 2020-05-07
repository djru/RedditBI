from flask_sqlalchemy import SQLAlchemy
import time

timestamp = lambda: int(time.time())


db = SQLAlchemy()
# https://flask-sqlalchemy.palletsprojects.com/en/2.x/api/?highlight=create_all#flask_sqlalchemy.BaseQuery
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column('id', db.Integer, primary_key=True, nullable=False, autoincrement=True)
    state = db.Column('state', db.String, index=True, nullable=False)
    code = db.Column('code', db.String, index=True, nullable=False)
    token = db.Column('token', db.String)
    refresh_token = db.Column('refresh_token', db.String)
    name = db.Column('name', db.String, index=True, unique=True)
    email = db.Column('email', db.String, unique=True)
    deleted_count = db.Column('deleted_count', db.Integer, default=0)
    confirmed = db.Column('text', db.String)
    updated = db.Column('updated', db.Integer, default=timestamp, onupdate=timestamp)

# TODO migrations

# NOTES
# https://hackersandslackers.com/flask-sqlalchemy-database-models/
# https://realpython.com/flask-by-example-part-2-postgres-sqlalchemy-and-alembic/

# https://stackoverflow.com/questions/1958219/convert-sqlalchemy-row-object-to-python-dict

if __name__ == '__main__':
    db.create_all()