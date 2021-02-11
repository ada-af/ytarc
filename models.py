from enum import unique
from config import db

class BaseModel:
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

class StorageObject(BaseModel, db.Model):
    title = db.Column(db.Text)
    description = db.Column(db.Text)
    filename = db.Column(db.String(256))
    preview = db.Column(db.String(256))
    original_filename = db.Column(db.String(1024))
    url = db.Column(db.Text, unique=True)
    origin = db.Column(db.String(32), default="remote")
    filetype = db.Column(db.String(64), default="other") # Music // Video // Image // Other
    sha256sum = db.Column(db.String(64))
    owned_by = db.Column(db.Integer, db.ForeignKey('link_object.id'))

class LinkObject(BaseModel, db.Model):
    link = db.Column(db.String(1024), unique=True)
    driver = db.Column(db.String(32), default='ddl') # ytdl - youtube-dl // ddl - direct download
    check_updates = db.Column(db.Boolean, default=False)
    linktype = db.Column(db.String(64), default='other')
    driver_options = db.Column(db.JSON)

class Tag(BaseModel, db.Model):
    name = db.Column(db.String(256))
    tagged_object = db.Column(db.Integer, db.ForeignKey("storage_object.id"))
    db.UniqueConstraint(name, tagged_object)
