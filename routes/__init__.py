from flask import Blueprint
from routes.api import ApiRoutes
from routes.web import routerWeb
from flask import render_template


api = Blueprint('api', __name__)
web = Blueprint('web', __name__)

# Đăng ký các route cho API
api_routes = ApiRoutes()
api.add_url_rule('/hello', view_func=api_routes.hello)

def hung(view):
    def h():
        return render_template(view)
    return h 

    
# Đăng ký các route cho Web
for router in routerWeb:
    web.add_url_rule(router.get('path'), view_func=hung(router.get('view')))


# for i in range(1):
#     web.add_url_rule('/', view_func=web_routes.index)
#     web.add_url_rule('/page1', view_func=web_routes.page1)
#     web.add_url_rule('/page2', view_func=web_routes.page2)