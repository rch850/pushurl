from flask import Flask
import settings

app = Flask('pushurl')
app.config.from_object('pushurl.settings')

import views

