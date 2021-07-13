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

class OrgDetail(Document):
  org = ReferenceField(Organization)
  creator = ReferenceField(User)
  public_id = StringField(default=public_id)
  created_on = DateTimeField(default=datetime.now)
  org_address = StringField(max_length=1024)
  org_email = EmailField(max_length=150)
  org_phone = IntField(min_value=0)
  org_notification = StringField(max_length=200)
  org_banner_name = StringField(max_length=50)
  org_banner_path = StringField(max_length=200)
  org_banner_link = StringField(max_length=200)


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