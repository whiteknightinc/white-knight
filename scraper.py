import praw
from requests import HTTPError
from praw.errors import RedirectException


def method():
    return fake()

def fake():
    return 3


def from_reddit(subreddit, subnumber):
        r = praw.Reddit('Whiteknight scrapping reddit for nasty comments'
                    'Url: https://github.com/whiteknightinc/white-knight')
        submission = r.get_subreddit(subreddit)
        comments = r.get_comments(submission, limit=subnumber)
        return comments


def get_comments(subreddit='all', subnumber=500):
    # top_posts = r.get_subreddit(subreddit).get_hot(limit=subnumber)
    result = {}
    comments = from_reddit(subreddit, subnumber)
    f = open("swearWordsValue.txt")
    keywords = {}
    for line in f:
        word, val = line.rstrip().split(",")
        keywords[word] = int(val)
    f.close()

    # for top_post in top_posts:
    #     submission = r.get_submission(submission_id=top_post.id)
    #     submission.replace_more_comments(limit=32, threshold=0)
    #     all_comments = submission.comments
    #     comments = praw.helpers.flatten_tree(all_comments)
    index = 0
    count = 0
    try:
        for comment in comments:
            print comment
            print count
            count += 1
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

    # result = {}
    # for num in range(len(comments_with_keywords)):
    #     result[num] = {}
    #     result[num]['text'] = comments_with_keywords[num].body
    #     result[num]['user'] = comments_with_keywords[num].author.name
    #     result[num]['permalink'] = comments_with_keywords[num].permalink
    return result


def make_nasty_comment(comment):
    user = comment.author.name
    permalink = comment.permalink
    dictcomment = {
        'text': comment.body,
        'user': user,
        'permalink': permalink
    }
    return dictcomment


def post_to_reddit(post):
    r = praw.Reddit('Whiteknight scrapping reddit for nasty comments'
                    'Url: https://github.com/whiteknightinc/white-knight')
    r.login(username='whiteknightinc', password='whiteknight123')

if __name__ == '__main__':
    entries = get_comments('whiteknighttest', 5)
    for num in entries:
        print entries[num]['text']
