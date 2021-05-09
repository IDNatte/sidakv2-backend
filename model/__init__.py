from datetime import datetime
from mongoengine import *
import secrets
import string

def public_id():
  a = string.ascii_letters + string.digits
  return ''.join(secrets.choice(a) for i in range(10))

class SectoralGroup(Document):
  sector_name = StringField(required=True)

class Organization(Document):
  org_name = StringField(required=True)
  sector_group = ReferenceField(SectoralGroup)

class User(Document):
  username = StringField(max_length=30, required=True, unique=True)
  email = EmailField(max_length=150, required=True, unique=True)
  password = StringField(max_length= 150, required=True, unique=True)
  is_active = BooleanField(required=True)
  org = ReferenceField(Organization)
  lvl = IntField(required=True)

class DynamicData(DynamicDocument):
  public_id = StringField(default=public_id)
  created_on = DateTimeField(default=datetime.now)
  owner = ReferenceField(User)
  table_name = StringField(required=True, unique=True)
  table_desc = StringField(required=True)

  meta = {
    'indexes': [
      {
        'fields': ['$table_name']
      }
    ]
  }