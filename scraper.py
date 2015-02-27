import praw
from requests import HTTPError
from praw.errors import RedirectException


def from_reddit(subreddit, subnumber):
        r = praw.Reddit('Whiteknight scrapping reddit for nasty comments'
                        'Url: https://github.com/whiteknightinc/white-knight')
        submission = r.get_subreddit(subreddit)
        comments = r.get_comments(submission, limit=subnumber)
        return comments


def get_comments(subreddit='all', subnumber=500):
    # top_posts = r.get_subreddit(subreddit).get_hot(limit=subnumber)
    """
    Get most recent [subnumber] comments from the specified subreddit.
    Return a dictionary of comments. Each comment is its own dictionary
    with username, text, and permalink.
    """
    result = {}
    comments = from_reddit(subreddit, subnumber)
    f = open("swearWordsValue.txt")
    keywords = {}
    for line in f:
        word, val = line.rstrip().split(",")
        keywords[word] = int(val)
    f.close()

    try:
        index = 0
        for comment in comments:
            score = 0
            comment_body = comment.body.lower()
            words = comment_body.split(' ')
            for word in words:
                word = word.rstrip('.')
                word = word.strip('"')
                word = word.rstrip('?')
                if word in keywords:
                    score += keywords.get(word)
                    if score >= 10:
                        result[index] = make_nasty_comment(comment)
                        index += 1
                        break
    except HTTPError:
        return {}
    except RedirectException:
        return {}

    return result


def make_nasty_comment(comment):
    """
    Turn a comment into a dictionary with its username, body, and permalink.
    """
    user = comment.author.name
    permalink = comment.permalink
    dictcomment = {
        'text': comment.body,
        'user': user,
        'permalink': permalink
    }
    return dictcomment
