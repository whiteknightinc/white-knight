import praw


def get_comments(subreddit, subnumber):
    r = praw.Reddit('Whiteknight scrapping reddit for nasty comments'
                    'Url: https://github.com/whiteknightinc/white-knight')

    # top_posts = r.get_subreddit(subreddit).get_hot(limit=subnumber)
    submission = r.get_subreddit('askreddit')
    comments = r.get_comments(submission, limit=1000)
    comments_with_keywords = []
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
    count = 0
    for comment in comments:
        print comment
        print count
        count += 1
        score = 0
        comment_body = comment.body.lower()
        words = comment_body.split(' ')
        length = len(comment_body) / 4
        for word in words:
            word = word.rstrip('.')
            word  = word.strip('"')
            word = word.rstrip('?')
            if word in keywords:
                score += keywords.get(word)
                if score >= 10 or score >= length:
                    comments_with_keywords.append(comment)
                    break

    result = {}
    for num in range(len(comments_with_keywords)):
        result[num] = {}
        result[num]['text'] = comments_with_keywords[num].body
        result[num]['user'] = comments_with_keywords[num].author.name
        result[num]['permalink'] = comments_with_keywords[num].permalink
    return result


def post_to_reddit(post):
    r = praw.Reddit('Whiteknight scrapping reddit for nasty comments'
                    'Url: https://github.com/whiteknightinc/white-knight')
    r.login(username='whiteknightinc', password='whiteknight123')

if __name__ == '__main__':
    entries = get_comments('whiteknighttest', 5)
    for num in entries:
        print entries[num]['text']
