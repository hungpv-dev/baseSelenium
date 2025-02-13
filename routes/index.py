from flask import Flask
from routes import api, web

app = Flask(__name__, static_folder='../static', template_folder='../static/html')

app.register_blueprint(web, url_prefix='/')
app.register_blueprint(api, url_prefix='/api')