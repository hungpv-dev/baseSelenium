from flask import Blueprint, render_template


views = Blueprint('views',__name__)

@views.route('/')
def home():
    return render_template("home.html")

@views.route('/page1')
def page1():
    return render_template("pages/page1.html")

@views.route('/page2')
def page2():
    return render_template("pages/page2.html")