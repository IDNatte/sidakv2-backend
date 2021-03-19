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

