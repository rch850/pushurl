from google.appengine.ext import db

class Page(db.Model):
    url = db.StringProperty(required = True)

