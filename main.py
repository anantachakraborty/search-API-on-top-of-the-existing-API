from flask import Flask, request, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def root():
    return """Welcome to the Comment Search API. Use /search to search for comments.<br>
    This API will serve the below requirements:--- <br>
    1. Comments can be searched with author name (search_author field).<br>
    2.Comments can be searched with a date range (at_from and at_to search fields).<br>
    3.Comments can be searched with reply and like count range (like_from, like_to, reply_from, reply_to fields).<br>
    4. Comments can be searched with a search string in the text field.(seach_text).<br>
    5. All the above searches can be done within the same requestas well."""


EXTERNAL_API_URL = "https://app.ylytic.com/ylytic/test"

def filter_comments(comments, search_author=None, at_from=None, at_to=None, like_from=None, like_to=None, reply_from=None, reply_to=None, search_text=None):
    filtered_comments = []
    for comment in comments:
        comment_date = datetime.strptime(comment['at'], '%a, %d %b %Y %H:%M:%S GMT')

        author_match = not search_author or search_author.lower() in comment['author'].lower()
        date_match = (not at_from or comment_date >= datetime.strptime(at_from, '%d-%m-%Y')) and \
                     (not at_to or comment_date <= datetime.strptime(at_to, '%d-%m-%Y'))
        like_match = (like_from is None or like_to is None) or \
                     (not like_from or comment['like'] >= int(like_from)) and \
                     (not like_to or comment['like'] <= int(like_to))
        reply_match = (reply_from is None or reply_to is None) or \
                      (not reply_from or comment['reply'] >= int(reply_from)) and \
                      (not reply_to or comment['reply'] <= int(reply_to))
        text_match = not search_text or search_text.lower() in comment['text'].lower()

        if author_match and date_match and like_match and reply_match and text_match:
            filtered_comments.append(comment)

    return filtered_comments

@app.route('/search', methods=['GET'])
def search_comments():
    search_author = request.args.get('search_author')
    at_from = request.args.get('at_from')
    at_to = request.args.get('at_to')
    like_from = request.args.get('like_from')
    like_to = request.args.get('like_to')
    reply_from = request.args.get('reply_from')
    reply_to = request.args.get('reply_to')
    search_text = request.args.get('search_text')

    params = {}
    if search_author:
        params['search_author'] = search_author
    if at_from:
        params['at_from'] = at_from
    if at_to:
        params['at_to'] = at_to
    if like_from:
        params['like_from'] = like_from
    if like_to:
        params['like_to'] = like_to
    if reply_from:
        params['reply_from'] = reply_from
    if reply_to:
        params['reply_to'] = reply_to
    if search_text:
        params['search_text'] = search_text

    try:
        response = requests.get(EXTERNAL_API_URL, params=params)
        response.raise_for_status()
        external_api_data = response.json()
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

    filtered_data = filter_comments(external_api_data['comments'], search_author, at_from, at_to, like_from, like_to, reply_from, reply_to, search_text)

    return jsonify({"comments": filtered_data})

if __name__ == '__main__':
    app.run(debug=True)
