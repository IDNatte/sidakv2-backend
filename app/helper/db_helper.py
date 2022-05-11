"""Database Helper Function"""


from werkzeug.security import generate_password_hash, check_password_hash
from bson import objectid
import uuid


def BSONObjectID():
    return objectid.ObjectId()


def UUIDGenerator():
    return str(uuid.uuid4())


def set_password(password):
    return generate_password_hash(password)


def check_password(authenticator, password):
    return check_password_hash(authenticator, password)
