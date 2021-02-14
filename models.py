from config import db

class BaseModel:
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    def __repr__(self):
        return f"=={self.__class__.__name__} {self.id}=="

class StorageObject(db.Model):
    id = db.Column(db.Integer, unique=True, default=lambda: len(StorageObject.query.all())+1 or 1)
    title = db.Column(db.Text)
    description = db.Column(db.Text)
    filename = db.Column(db.String(256))
    preview = db.Column(db.String(256))
    original_filename = db.Column(db.String(1024))
    url = db.Column(db.Text, primary_key=True)
    origin = db.Column(db.String(32), default="remote")
    filetype = db.Column(db.String(64), default="other") # Music // Video // Image // Other
    sha256sum = db.Column(db.String(64))
    owned_by = db.Column(db.Integer, db.ForeignKey('link_object.id'))

    def get_owner(self):
        return LinkObject.query.get(self.owned_by)
    
    def get_tags(self):
        return Tag.query.filter_by(tagged_object=self.id).all()

class LinkObject(BaseModel, db.Model):
    link = db.Column(db.String(1024), unique=True)
    driver = db.Column(db.String(32), default='ddl') # ytdl - youtube-dl // ddl - direct download
    check_updates = db.Column(db.Boolean, default=False)
    linktype = db.Column(db.String(64), default='other')
    driver_options = db.Column(db.JSON)

    def get_options(self):
        return ", ".join([f"{x}={self.driver_options[x]}" for x in self.driver_options.keys()])

class Tag(BaseModel, db.Model):
    name = db.Column(db.String(256))
    tagged_object = db.Column(db.Integer, db.ForeignKey("storage_object.id"))
    db.UniqueConstraint(name, tagged_object)
