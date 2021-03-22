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
  content = db.relationship('FileEntry', backref='user')

  def set_password(self, raw_passwd):
    self.password = generate_password_hash(raw_passwd)

  def check_password(self, raw_passwd):
    return check_password_hash(self.password, raw_passwd)

class FileEntry(db.Model):
  __tablename__ = 'file_entry'
  fid = db.Column(db.String, default = dbhelper.UUIDGenerator(), primary_key=True)
  created_by = db.Column(db.DateTime, default = datetime.utcnow())
  fileURL = db.Column(db.String(255), nullable = False)
  owner = db.Column(db.String, db.ForeignKey('user.uid'))