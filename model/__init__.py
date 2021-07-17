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
  sector_group = ReferenceField(SectoralGroup, reverse_delete_rule=CASCADE)

class User(Document):
  username = StringField(max_length=30, required=True, unique=True)
  email = EmailField(max_length=150, required=True, unique=True)
  password = StringField(max_length= 150, required=True, unique=True)
  is_active = BooleanField(required=True)
  org = ReferenceField(Organization, reverse_delete_rule=CASCADE)
  lvl = IntField(required=True)

class OrgDetail(Document):
  org = ReferenceField(Organization, reverse_delete_rule=CASCADE)
  creator = ReferenceField(User, reverse_delete_rule=CASCADE)
  public_id = StringField(default=public_id)
  created_on = DateTimeField(default=datetime.now)
  org_address = StringField(max_length=1024)
  org_email = EmailField(max_length=150, unique=True)
  org_phone = StringField(max_length=200)
  org_notification = StringField(max_length=200)


class OrgDetailBanner(Document):
  org_detail = ReferenceField(OrgDetail, reverse_delete_rule=CASCADE)
  org_public_id = StringField(default=public_id)
  org_banner_name = StringField(max_length=50)
  org_banner_path = StringField(max_length=200)
  org_banner_url = StringField(max_length=255)


class DynamicData(DynamicDocument):
  public_id = StringField(default=public_id)
  created_on = DateTimeField(default=datetime.now)
  owner = ReferenceField(User, reverse_delete_rule=CASCADE)
  table_name = StringField(required=True, unique=True)
  table_desc = StringField(required=True)

  meta = {
    'indexes': [
      {
        'fields': ['$table_name']
      }
    ]
  }