from flask import Flask

def create_app():
    app = Flask(__name__, static_folder='../static', template_folder='../templates')

    # Thiết lập secret_key
    app.secret_key = 'iYGqlLXXhs'

    from .views import views
    from .api import api
    from .spy_browse import spy_browse
    
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(spy_browse, url_prefix='/spy-browse')
    app.register_blueprint(api, url_prefix='/api')

    return app

def start_app(app):
    app.run(debug=True, use_reloader=False)