from flask import Flask

def create_app():
    app = Flask(__name__, static_folder='../static', template_folder='../templates')

    from .views import views
    
    app.register_blueprint(views, url_prefix='/')

    return app

def start_app(app):
    app.run(debug=True, use_reloader=False)