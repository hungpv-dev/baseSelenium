from flask import Blueprint, render_template
from sql import accounts, posts
from stores import browse_fb

views = Blueprint('views',__name__)

@views.route('/')
def home():
    return render_template("home.html")


@views.route('/posts')
def list_posts():
    list_posts = posts.get() 
    unique_fb_links = set()
    filtered_posts = []
    duplicate_count = 0  
    total_duplicates = 0 

    for post in list_posts:
        if post.get('fb_link') not in unique_fb_links:
            unique_fb_links.add(post.get('fb_link'))
            filtered_posts.append(post)
        else:
            duplicate_count += 1
        total_duplicates += 1

    return render_template(
        "pages/posts.html",
        list_posts=filtered_posts, 
        unique_count=len(filtered_posts),
        duplicate_count=duplicate_count, 
        total_duplicates=total_duplicates 
    )


@views.route('/accounts')
def list_account():
    list_accounts = accounts.get()
    for acc in list_accounts:
        if acc.get('id') in browse_fb and browse_fb[acc.get('id')]['thread'].is_alive():
            acc['is_browse_link_fb'] = 1 
        else:
            acc['is_browse_link_fb'] = 2 
    return render_template("pages/accounts.html",list_accounts=list_accounts)