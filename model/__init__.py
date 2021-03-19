from werkzeug.security import generate_password_hash, check_password_hash
from config import db


class User(db.Model):

  uid = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String(255), nullable=False)
  password = db.Column(db.String(255), nullable=False)
  username = db.Column(db.String(30), nullable=False, unique=True)

  def set_password(self, raw_passwd):
    self.password = generate_password_hash(raw_passwd)

  def check_password(self, raw_passwd):
    return check_password_hash(self.password, raw_passwd)



# from werkzeug.security import generate_password_hash, check_password_hash
# from sqlalchemy import Column, ForeignKey, Integer, String
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import relationship
# from sqlalchemy import create_engine
# import sys

# Base = declarative_base()

# class User(Base):
#   __tablename__ = 'user'

#   uid = Column(Integer, primary_key=True)
#   email = Column(String(255), nullable=False)
#   password = Column(String(255), nullable=False)
#   username = Column(String(30), nullable=False, unique=True)

#   def set_password(self, raw_passwd):
#     self.password = generate_password_hash(raw_passwd)

#   def check_password(self, raw_passwd):
#     return check_password_hash(self.password, raw_passwd)

#   @property
#   def serialize(self):
#     return {
#       'uid': self.uid,
#       'username': self.username,
#       'email': self.email
#     }

# engine = create_engine('sqlite:///db/database.db')
# Base.metadata.create_all(engine)

