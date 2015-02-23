import praw

r = praw.Reddit('Whiteknight scrapping reddit for nasty comments'
                'Url: https://github.com/whiteknightinc/white-knight')
# r.login()

top_posts = r.get_subreddit('all').get_hot(limit=1)
keywords = ['fuck', 'shit', 'damn']
comments_with_keywords = []

for top_post in top_posts:
    submission = r.get_submission(submission_id=top_post.id)
    submission.replace_more_comments(limit=5, threshold=0)
    all_comments = submission.comments
    comments = praw.helpers.flatten_tree(all_comments)

    for comment in comments:
        # print comment.body
        words = comment.body.lower()
        for keyword in keywords:
            if keyword in words:
                comments_with_keywords.append(comment)


