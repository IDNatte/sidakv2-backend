from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from model import dbhelper
from config import db

class User(db.Model):
  __tablename__ = 'user'
  uid = db.Column(db.String, primary_key=True, default=dbhelper.UUIDGenerator())
  email = db.Column(db.String(255), nullable=False)
  password = db.Column(db.String(255), nullable=False)
  username = db.Column(db.String(30), nullable=False, unique=True)
  org = db.Column(db.String(50), nullable=False)
  content = db.relationship('UserFileEntry', backref='user', cascade="all, delete-orphan")

  def set_password(self, raw_passwd):
    self.password = generate_password_hash(raw_passwd)

  def check_password(self, raw_passwd):
    return check_password_hash(self.password, raw_passwd)

class UserFileEntry(db.Model):
  __tablename__ = 'u_file_entry'
  ufid = db.Column(db.String, default = dbhelper.UUIDGenerator(), primary_key=True)
  created_on = db.Column(db.DateTime, default = datetime.utcnow())
  fileURL = db.Column(db.String(255), nullable = False)
  owner = db.Column(db.String, db.ForeignKey('user.uid'))

# class GlobalFileEntry(db.Model):
#   __tablenaem__ = 'g_file_entry'
#   gfid = db.Column(db.String, default = dbhelper.UUIDGenerator(), primary_key=True)
#   fileURL = db.Column(db.String(255), nullable = False)
#   created