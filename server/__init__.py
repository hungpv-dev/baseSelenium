from flask import Flask, render_template
from flask_session import Session

def create_app():
    app = Flask(__name__, static_folder='../static', template_folder='../templates')

    # Thiết lập secret_key
    # Thiết lập secret_key
    app.secret_key = 'iYGqlLXXhs'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['JWT_SECRET_KEY'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c'  # Thay thế bằng khóa bí mật của bạn
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 900  # Access token hết hạn sau 15 phút
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = 86400  # Refresh token hết hạn sau 1 ngày
    Session(app)

    from .views import views
    from .profiles import profiles
    from .settings import settings
    from .driver import drivers
    from .groups import group
    from .api import api
    from .fakeagent import useragent
    from .accounts import account
    from .proxies import proxy
    from .automation import crawl_ads


    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(profiles, url_prefix='/api/profiles')
    app.register_blueprint(group, url_prefix='/api/groups')
    app.register_blueprint(account, url_prefix='/api/accounts')
    app.register_blueprint(proxy, url_prefix='/api/proxies')
    app.register_blueprint(useragent, url_prefix='/api/useragent')
    app.register_blueprint(drivers, url_prefix='/api/driver')
    app.register_blueprint(settings, url_prefix='/api/settings')
    app.register_blueprint(crawl_ads, url_prefix='/tools/crawl-ads')

    app.jinja_env.variable_start_string = '[['
    app.jinja_env.variable_end_string = ']]'

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404
    
    
    return app

def start_app(app, reload=True):
    app.run(debug=True, use_reloader=reload)