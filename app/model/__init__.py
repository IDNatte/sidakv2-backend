"""Model class"""

from app.helper.randomizer import random_public_id
from datetime import datetime
from app.shared import DB


class SectoralGroup(DB.Document):
    sector_name = DB.StringField(required=True)


class Organization(DB.Document):
    org_name = DB.StringField(required=True)
    sector_group = DB.ReferenceField(
        SectoralGroup, reverse_delete_rule=DB.CASCADE)


class User(DB.Document):
    username = DB.StringField(max_length=30, required=True, unique=True)
    email = DB.EmailField(max_length=150, required=True, unique=True)
    password = DB.StringField(max_length=150, required=True, unique=True)
    is_active = DB.BooleanField(required=True)
    org = DB.ReferenceField(Organization, reverse_delete_rule=DB.CASCADE)
    lvl = DB.IntField(required=True)


class OrgDetail(DB.Document):
    org = DB.ReferenceField(Organization, reverse_delete_rule=DB.CASCADE)
    creator = DB.ReferenceField(User, reverse_delete_rule=DB.CASCADE)
    public_id = DB.StringField(default=random_public_id)
    created_on = DB.DateTimeField(default=datetime.now)
    org_address = DB.StringField(max_length=1024)
    org_email = DB.EmailField(max_length=150, unique=True)
    org_phone = DB.StringField(max_length=200)
    org_notification = DB.StringField(max_length=200)


class OrgDetailBanner(DB.Document):
    org_detail = DB.ReferenceField(OrgDetail, reverse_delete_rule=DB.CASCADE)
    org_public_id = DB.StringField(default=random_public_id)
    org_banner_name = DB.StringField(max_length=50)
    org_banner_path = DB.StringField(max_length=200)
    org_banner_url = DB.StringField(max_length=255)


class DynamicData(DB.DynamicDocument):
    public_id = DB.StringField(default=random_public_id)
    created_on = DB.DateTimeField(default=datetime.now)
    owner = DB.ReferenceField(User, reverse_delete_rule=DB.CASCADE)
    table_name = DB.StringField(required=True, unique=True)
    table_desc = DB.StringField(required=True)

    meta = {
        'indexes': [
            {
                'fields': ['$table_name']
            }
        ]
    }


# class
