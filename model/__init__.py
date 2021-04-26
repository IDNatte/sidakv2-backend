from datetime import datetime
from mongoengine import *

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
  created_on = DateTimeField(default=datetime.now())
  owner = ReferenceField(User)
  table_name = StringField(required=True, unique=True)
  table_desc = StringField(required=True)
