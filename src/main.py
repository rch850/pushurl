import sys
sys.path.insert(0, "./libs")

from google.appengine.ext.webapp.util import run_wsgi_app
from pushurl import app

run_wsgi_app(app)
