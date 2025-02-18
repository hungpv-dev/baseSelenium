from flask import Blueprint, render_template
from sql import accounts, posts
from stores import browse_fb

views = Blueprint('views',__name__)

@views.route('/')
def home():
    return render_template("home.html")


@views.route('/posts')
def list_posts():
    return render_template("pages/posts.html")


@views.route('/accounts')
def list_account():
    list_accounts = accounts.get()
    for acc in list_accounts:
        if acc.get('id') in browse_fb and browse_fb[acc.get('id')]['thread'].is_alive():
            acc['is_browse_link_fb'] = 1 
        else:
            acc['is_browse_link_fb'] = 2 
    return render_template("pages/accounts.html",list_accounts=list_accounts)