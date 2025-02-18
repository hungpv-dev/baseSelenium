from flask import Blueprint, jsonify
from sql import accounts, posts
from stores import browse_fb

api = Blueprint('api',__name__)

@api.route('/posts')
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

    return jsonify({
        'list_posts': filtered_posts, 
        'unique_count': len(filtered_posts),
        'duplicate_count': duplicate_count,
        'total_duplicates': total_duplicates 
    })

@api.route('/accounts')
def list_account():
    list_accounts = accounts.get()
    for acc in list_accounts:
        if acc.get('id') in browse_fb and browse_fb[acc.get('id')]['thread'].is_alive():
            acc['is_browse_link_fb'] = 1 
        else:
            acc['is_browse_link_fb'] = 2 

    return jsonify(list_accounts)
    