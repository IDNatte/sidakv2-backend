from pymongo import MongoClient
from model import dbhelper
from bson import objectid


cl = MongoClient("mongodb://admin:admin123@localhost/sisv_db?authSource=admin")
db = cl.sisv_db

sector_group = db.sectoral_group
organization = db.organization
user = db.user

# create sector
s = sector_group.insert({"sector_name": "Sektor Sosial"})
o = organization.insert({"org_name": "Dinas Kominfo", "sector_group": s})
user.insert({"username": "admin", "email": "admin@admin.com", "password": dbhelper.set_password('admin123'), 'lvl': 1, "org": o, "is_active": True})