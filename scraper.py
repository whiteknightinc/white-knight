import praw


def get_comments():
    r = praw.Reddit('Whiteknight scrapping reddit for nasty comments'
                    'Url: https://github.com/whiteknightinc/white-knight')

    top_posts = r.get_subreddit('whiteknighttest').get_top(limit=10)
    comments_with_keywords = []
    f = open("swearWords.txt")
    keywords = []
    for line in f:
        keywords.append(line.rstrip())
    f.close()

    for top_post in top_posts:
        submission = r.get_submission(submission_id=top_post.id)
        submission.replace_more_comments(limit=32, threshold=0)
        all_comments = submission.comments
        comments = praw.helpers.flatten_tree(all_comments)

        for comment in comments:
            words = comment.body.lower()
            for keyword in keywords:
                if keyword in words:
                    comments_with_keywords.append(comment)
                    break

    result = {}
    for num in range(len(comments_with_keywords)):
        result[num] = {}
        result[num]['text'] = comments_with_keywords[num].body
        result[num]['user'] = comments_with_keywords[num].author.name
        result[num]['permalink'] = comments_with_keywords[num].permalink
    return result

if __name__ == '__main__':
    entries = get_comments()
    for num in entries:
        print entries[num]['permalink']
