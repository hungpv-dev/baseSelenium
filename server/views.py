from flask import Blueprint, render_template,session,redirect, url_for
from sql import accounts, posts
from stores import browse_fb
from functools import wraps
views = Blueprint('views',__name__)
# def login_required_session(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if 'user' not in session:
#             return redirect(url_for('views.authLogin'))  # Updated endpoint
#         return f(*args, **kwargs)
#     return decorated_function
@views.route('/')
# @login_required_session
def home():
    return render_template("home.html")


@views.route('/posts')
# @login_required_session
def list_posts():
    return render_template("pages/posts.html")


@views.route('/accounts')
# @login_required_session
def list_account():
    list_accounts = accounts.get()
    for acc in list_accounts:
        if acc.get('id') in browse_fb and browse_fb[acc.get('id')]['thread'].is_alive():
            acc['is_browse_link_fb'] = 1 
        else:
            acc['is_browse_link_fb'] = 2 
    return render_template("pages/accounts.html",list_accounts=list_accounts)

@views.route('/settings')
# @login_required_session
def settings():
    return render_template("pages/settings.html")


@views.route('/profiles')
# @login_required_session
def profiles():
    return render_template("pages/profiles/list.html")


@views.route('/profiles/create')
# @login_required_session
def profile_create():
    return render_template("pages/profiles/create.html")
@views.route("/login")
def authLogin():
    return render_template("pages/authen/login.html")
@views.route('/groups')
# @login_required_session
def groups():
    return render_template("pages/profiles/groups.html")

@views.route('/crawl-ads')
# @login_required_session
def crawlAds():
    return render_template("pages/automations/crawl-ads.html")