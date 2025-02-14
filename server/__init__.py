from flask import Flask

def create_app():
    app = Flask(__name__, static_folder='../static', template_folder='../templates')

    from .views import views
    from .driver import driver
    
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(driver, url_prefix='/driver')

    return app

def start_app(app):
    app.run(debug=True, use_reloader=False)